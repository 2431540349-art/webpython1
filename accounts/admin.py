from django.contrib import admin
from .models import Course
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .tasks import send_study_reminders_for_course
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import AdminSite
from django.conf import settings
import os
from .models import (
    Course, Enrollment, Lesson, Question, Choice, LessonProgress,
    MockExam, MockQuestion, MockChoice, ExamAttempt,
    SpeakingSubmission, WritingSubmission
)
from .models import SentEmail
from .admin_site import admin_site

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4  # Hiển thị 4 lựa chọn mặc định (a, b, c, d)

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    # Note: Django admin doesn't support nested inlines out of the box.
    # Keep this inline for adding/editing Questions when editing a Lesson.
    # To add/edit Choices, open the Question in the Question admin (below).

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_info', 'get_enrolled_count', 'get_lessons_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    inlines = [LessonInline]
    
    fieldsets = (
        ('Thông tin khóa học', {
            'fields': ('title', 'description', 'image'),
            'classes': ('wide',)
        }),
        ('Thống kê', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)

    def course_info(self, obj):
        image_html = ''
        if obj.image:
            image_html = format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:4px;margin-right:10px">',
                obj.image.url
            )
        return format_html(
            '<div style="display:flex;align-items:center">{}'
            '<div><strong style="font-size:1.1em">{}</strong><br>'
            '<span style="color:#666">{}</span></div></div>',
            image_html, obj.title,
            obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
        )
    course_info.short_description = 'Khóa học'

    def get_lessons_count(self, obj):
        count = obj.lessons.count()
        return format_html(
            '<span class="badge" style="background:#1a73e8">{} bài học</span>',
            count
        )
    get_lessons_count.short_description = 'Bài học'

    def get_enrolled_count(self, obj):
        count = obj.enrolled_users.count()
        return format_html(
            '<span class="badge" style="background:#34a853">{} học viên</span>',
            count
        )
    get_enrolled_count.short_description = 'Học viên đăng ký'

    # Admin action to send reminders for this course (selected in changelist)
    actions = ['send_reminders_for_selected']

    def send_reminders_for_selected(self, request, queryset):
        count = 0
        for course in queryset:
            try:
                send_study_reminders_for_course.delay(course.id)
                count += 1
            except Exception:
                # fallback synchronous
                send_study_reminders_for_course(course.id)
                count += 1
        self.message_user(request, _('%d reminder job(s) queued or executed.') % count, level=messages.SUCCESS)

    send_reminders_for_selected.short_description = 'Send reminders for selected courses'

    class Media:
        css = {
            'all': ('accounts/admin/css/custom_admin.css',)
        }

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'get_questions_count', 'video')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [QuestionInline]
    ordering = ['course', 'order']

    def get_questions_count(self, obj):
        return obj.questions.count()
    get_questions_count.short_description = 'Số câu hỏi'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'lesson', 'order')
    list_filter = ('lesson__course', 'lesson')
    search_fields = ('question_text',)
    inlines = [ChoiceInline]
    ordering = ['lesson', 'order']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('user__username', 'course__title')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'score', 'completed_at')
    list_filter = ('completed', 'lesson__course')
    search_fields = ('user__username', 'lesson__title')


class MockChoiceInline(admin.TabularInline):
    model = MockChoice
    extra = 4


@admin.register(MockExam)
class MockExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_type_display', 'skill_display', 'question_count', 'created_at')
    list_filter = ('exam_type', 'skill', 'created_at')
    search_fields = ('title', 'description')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'exam_type', 'skill')
        }),
        ('Mô tả chi tiết', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )

    def exam_type_display(self, obj):
        return format_html(
            '<span class="badge" style="background:{}">{}</span>',
            '#1a73e8' if obj.exam_type == 'ielts' else '#34a853',
            obj.get_exam_type_display()
        )
    exam_type_display.short_description = 'Loại bài thi'

    def skill_display(self, obj):
        colors = {
            'listening': '#fbbc04',
            'speaking': '#ea4335',
            'reading': '#1a73e8',
            'writing': '#34a853'
        }
        return format_html(
            '<span class="badge" style="background:{}">{}</span>',
            colors.get(obj.skill, '#666'),
            obj.get_skill_display()
        )
    skill_display.short_description = 'Kỹ năng'

    def question_count(self, obj):
        count = obj.questions.count()
        return format_html(
            '{} câu hỏi',
            count
        )
    question_count.short_description = 'Số câu hỏi'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(MockQuestion)
class MockQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam_info', 'order', 'has_sample_answer', 'media_preview')
    list_filter = ('exam__exam_type', 'exam__skill')
    search_fields = ('text', 'exam__title')
    fields = (
        'exam', 'text', 'order',
        ('media_file', 'media_preview'),
        'sample_answer'
    )
    readonly_fields = ('media_preview',)
    inlines = [MockChoiceInline]

    def exam_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><span style="color: #666">{} - {}</span>',
            obj.exam.title,
            obj.exam.get_exam_type_display(),
            obj.exam.get_skill_display()
        )
    exam_info.short_description = 'Bài thi'

    def has_sample_answer(self, obj):
        # Use getattr to avoid AttributeError if the field isn't present yet (migration not applied)
        return bool(getattr(obj, 'sample_answer', None))
    has_sample_answer.short_description = 'Có câu mẫu'
    has_sample_answer.boolean = True

    def media_preview(self, obj):
        if not obj.media_file:
            return 'Không có tệp'
        if obj.media_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 300px;">',
                obj.media_file.url
            )
        elif obj.media_file.name.lower().endswith(('.mp3', '.wav', '.ogg')):
            return format_html(
                '<audio controls style="max-width:300px"><source src="{}"></audio>',
                obj.media_file.url
            )
        return format_html('<a href="{}">Tải xuống tệp</a>', obj.media_file.url)
    media_preview.short_description = 'Xem trước'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score', 'created_at')
    list_filter = ('exam', 'created_at')
    search_fields = ('user__username', 'exam__title')


@admin.register(SpeakingSubmission)
class SpeakingSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'reviewed', 'score', 'created_at')
    list_filter = ('reviewed', 'created_at')
    search_fields = ('user__username', 'question__text')


@admin.register(WritingSubmission)
class WritingSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'reviewed', 'score', 'created_at')
    list_filter = ('reviewed', 'created_at')
    search_fields = ('user__username', 'question__text')

    # Also register the same ModelAdmin classes with the custom admin_site instance
try:
    admin_site.register(Course, CourseAdmin)
    admin_site.register(Lesson, LessonAdmin)
    admin_site.register(Question, QuestionAdmin)
    admin_site.register(Enrollment, EnrollmentAdmin)
    admin_site.register(LessonProgress, LessonProgressAdmin)
    admin_site.register(MockExam, MockExamAdmin)
    admin_site.register(MockQuestion, MockQuestionAdmin)
    admin_site.register(ExamAttempt, ExamAttemptAdmin)
    admin_site.register(SpeakingSubmission, SpeakingSubmissionAdmin)
    admin_site.register(WritingSubmission, WritingSubmissionAdmin)
    # Register SentEmail for admin visibility and resend capability
    class SentEmailAdmin(admin.ModelAdmin):
        list_display = ('to_email', 'subject', 'course', 'sent_at', 'status')
        list_filter = ('status', 'sent_at', 'course')
        search_fields = ('to_email', 'subject', 'body')
        readonly_fields = ('sent_at', 'body')
        actions = ['resend_selected_emails']
        
        def resend_selected_emails(self, request, queryset):
            """Resend selected emails by creating new task records."""
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            
            resent_count = 0
            error_count = 0
            
            for sent_email in queryset:
                try:
                    # Resend the email
                    send_mail(
                        subject=sent_email.subject,
                        message='',
                        html_message=sent_email.body,
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                        recipient_list=[sent_email.to_email],
                        fail_silently=False,
                    )
                    # Create a new SentEmail record for this resend
                    SentEmail.objects.create(
                        to_email=sent_email.to_email,
                        subject=sent_email.subject + ' (Resent)',
                        body=sent_email.body,
                        course=sent_email.course,
                        status='sent'
                    )
                    resent_count += 1
                except Exception as exc:
                    error_count += 1
                    SentEmail.objects.create(
                        to_email=sent_email.to_email,
                        subject=sent_email.subject + ' (Resent - Failed)',
                        body=str(exc)[:200],
                        course=sent_email.course,
                        status=f'error: {type(exc).__name__}'
                    )
            
            self.message_user(
                request,
                _('%d email(s) resent successfully. %d error(s).') % (resent_count, error_count),
                level=messages.SUCCESS if error_count == 0 else messages.WARNING
            )
        
        resend_selected_emails.short_description = 'Resend selected emails'

    admin_site.register(SentEmail, SentEmailAdmin)
except Exception:
    # If a model is already registered or registration fails, don't crash import
    pass
