from django.urls import reverse

def user_progress(request):
    """Context processor that returns a summary of the user's progress
    for each enrolled course. Added to templates so the navbar can show
    per-course progress for the logged-in user.

    Returns:
        {'user_progress': [
            {'id': int, 'title': str, 'percent': int, 'completed': int, 'total': int, 'url': str},
            ...
        ]}
    """
    if not request.user.is_authenticated:
        return {}

    try:
        from .models import Course, LessonProgress
    except Exception:
        # If models can't be imported for any reason (tests etc.), fail gracefully
        return {}

    courses = Course.objects.filter(enrolled_users=request.user).distinct()
    progress_list = []
    for course in courses:
        total = course.lessons.count()
        if total == 0:
            percent = 0
            completed = 0
        else:
            completed = LessonProgress.objects.filter(
                user=request.user,
                lesson__course=course,
                completed=True
            ).count()
            percent = int((completed / total) * 100)

        progress_list.append({
            'id': course.id,
            'title': course.title,
            'percent': percent,
            'completed': completed,
            'total': total,
            'url': reverse('accounts:course_detail', args=[course.id])
        })

    return {'user_progress': progress_list}
