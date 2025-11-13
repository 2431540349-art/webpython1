from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Import signal handlers to keep admin grading in sync with ExamAttempt
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid import-time failures preventing startup; admin can still work.
            pass
