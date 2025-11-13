from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from .models import Enrollment, LessonProgress, Course
from .models import SentEmail
import logging
from social_django.models import UserSocialAuth

User = get_user_model()

@shared_task
def send_daily_schedule():
    """
    Send daily schedule to all users
    """
    today = timezone.now().date()
    
    # Get all users with email addresses
    users = User.objects.filter(email__isnull=False).exclude(email='')
    
    for user in users:
        # Get user's schedule for today
        schedules = user.student.schedule_set.filter(date=today).select_related('course')
        
        if schedules.exists():
            # Prepare email content
            context = {
                'user': user,
                'schedules': schedules,
                'date': today,
            }
            
            # Render email content from template
            html_content = render_to_string('email/daily_schedule.html', context)
            
            # Send email
            send_mail(
                subject=f'Lịch học ngày {today.strftime("%d/%m/%Y")}',
                message='',
                html_message=html_content,
                from_email='your-email@gmail.com',
                recipient_list=[user.email],
                fail_silently=False,
            )


@shared_task
def send_study_reminders():
    """
    Send study reminder emails to users who authenticated via Google (social login).

    Behavior:
    - Finds users that have a Google social auth (provider 'google-oauth2').
    - For each user, finds enrolled courses where the user hasn't completed all lessons.
    - Sends an email listing pending courses, progress, and a link to continue studying.

    Notes:
    - Uses `settings.SITE_URL` as the absolute site prefix when present; otherwise email contains relative links.
    - Uses Django's configured EMAIL_BACKEND; in development it's `console` by default.
    """
    site_prefix = getattr(settings, 'SITE_URL', '').rstrip('/')
    User = get_user_model()
    # users with a google social auth entry
    google_users = User.objects.filter(
        id__in=UserSocialAuth.objects.filter(provider__in=('google-oauth2', 'google-openidconnect')).values_list('user_id', flat=True)
    )

    for user in google_users:
        if not user.email:
            continue

        # find enrolled courses for this user
        enrollments = Enrollment.objects.filter(user=user).select_related('course')
        pending = []
        for e in enrollments:
            course = e.course
            lessons = course.lessons.all().order_by('order')
            total = lessons.count()
            if total == 0:
                continue
            completed_count = LessonProgress.objects.filter(user=user, lesson__course=course, completed=True).count()
            if completed_count >= total:
                continue
            next_lesson = None
            for l in lessons:
                lp = LessonProgress.objects.filter(user=user, lesson=l).first()
                if not lp or not lp.completed:
                    next_lesson = l
                    break
            progress_percent = int((completed_count / total) * 100) if total > 0 else 0
            pending.append({
                'course': course,
                'progress': progress_percent,
                'next_lesson': next_lesson,
                'course_url': f"{site_prefix}/accounts/course/{course.id}/" if site_prefix else f"/accounts/course/{course.id}/",
            })

        if not pending:
            continue

        context = {
            'user': user,
            'pending': pending,
        }

        html_message = render_to_string('email/study_reminder.html', context)
        subject = 'Nhắc học: Tiến độ khóa học của bạn'

        try:
            send_mail(
                subject=subject,
                message='',
                html_message=html_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[user.email],
                fail_silently=False,
            )
            # record sent email
            try:
                SentEmail.objects.create(
                    to_email=user.email,
                    subject=subject,
                    body=html_message,
                    course=None,
                    status='sent'
                )
            except Exception:
                logging.exception('Failed to create SentEmail record for %s', user.email)
        except Exception as exc:
            logging.exception('Failed to send reminder to %s', user.email)
            try:
                SentEmail.objects.create(
                    to_email=user.email,
                    subject=subject,
                    body=str(exc)[:200],
                    course=None,
                    status=f'error: {type(exc).__name__}'
                )
            except Exception:
                logging.exception('Failed to create error SentEmail record for %s', user.email)


@shared_task
def send_study_reminders_for_course(course_id):
    """Send reminders only for users enrolled in the given course id."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        course = Course.objects.get(id=course_id)
    except Exception:
        return

    # users enrolled in this course
    enrollments = Enrollment.objects.filter(course=course).select_related('user')
    users = [e.user for e in enrollments]

    site_prefix = getattr(settings, 'SITE_URL', '').rstrip('/')

    for user in users:
        if not user.email:
            continue
        lessons = course.lessons.all().order_by('order')
        total = lessons.count()
        completed_count = LessonProgress.objects.filter(user=user, lesson__course=course, completed=True).count()
        if completed_count >= total:
            continue
        next_lesson = None
        for l in lessons:
            lp = LessonProgress.objects.filter(user=user, lesson=l).first()
            if not lp or not lp.completed:
                next_lesson = l
                break
        progress_percent = int((completed_count / total) * 100) if total > 0 else 0
        context = {
            'user': user,
            'pending': [{
                'course': course,
                'progress': progress_percent,
                'next_lesson': next_lesson,
                'course_url': f"{site_prefix}/accounts/course/{course.id}/" if site_prefix else f"/accounts/course/{course.id}/",
            }]
        }
        html_message = render_to_string('email/study_reminder.html', context)
        subject = f'Nhắc học: {course.title} — tiến độ của bạn'
        try:
            send_mail(
                subject=subject,
                message='',
                html_message=html_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[user.email],
                fail_silently=False,
            )
            try:
                SentEmail.objects.create(
                    to_email=user.email,
                    subject=subject,
                    body=html_message,
                    course=course,
                    status='sent'
                )
            except Exception:
                logging.exception('Failed to create SentEmail record for %s (course)', user.email)
        except Exception as exc:
            logging.exception('Failed to send course reminder to %s', user.email)
            try:
                SentEmail.objects.create(
                    to_email=user.email,
                    subject=subject,
                    body=str(exc)[:200],
                    course=course,
                    status=f'error: {type(exc).__name__}'
                )
            except Exception:
                logging.exception('Failed to create error SentEmail record for %s (course)', user.email)