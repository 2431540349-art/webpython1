from django.core.management.base import BaseCommand
from django.conf import settings

def _create_crontab_and_task():
    try:
        from django_celery_beat.models import CrontabSchedule, PeriodicTask
    except Exception:
        return (False, 'django-celery-beat is not installed')

    # Daily at 09:00 server time
    schedule, created = CrontabSchedule.objects.get_or_create(minute='0', hour='9', day_of_week='*', day_of_month='*', month_of_year='*')

    task_name = 'accounts.tasks.send_study_reminders'
    pt, created = PeriodicTask.objects.get_or_create(
        name='daily-study-reminders',
        defaults={
            'crontab': schedule,
            'task': task_name,
            'enabled': True,
        }
    )
    if not created:
        # ensure crontab is set
        pt.crontab = schedule
        pt.task = task_name
        pt.enabled = True
        pt.save()

    return (True, 'Periodic task created or updated')


class Command(BaseCommand):
    help = 'Create a daily reminder periodic task (requires django-celery-beat and celery worker+beat running)'

    def handle(self, *args, **options):
        ok, msg = _create_crontab_and_task()
        if not ok:
            self.stdout.write(self.style.ERROR(msg))
            return
        self.stdout.write(self.style.SUCCESS(msg))
