from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WritingSubmission, SpeakingSubmission, ExamAttempt


@receiver(post_save, sender=WritingSubmission)
def update_attempt_on_writing_save(sender, instance, created, **kwargs):
    """When a writing submission is graded in admin, reflect the score on the related ExamAttempt.

    Strategy (minimal, non-breaking):
    - If the exam's skill is 'writing' (i.e. exam is writing-only), set the attempt.score to the
      writing submission score.
    - Otherwise, set the attempt.score to the max(existing_attempt_score, writing_score) so the
      student's displayed score does not decrease and at least shows the graded value.
    """
    # Only act if a score has been set
    if instance.score is None:
        return

    exam = instance.question.exam
    try:
        attempt = ExamAttempt.objects.filter(user=instance.user, exam=exam).order_by('-created_at').first()
        if not attempt:
            return

        if exam.skill == 'writing':
            attempt.score = instance.score
        else:
            # conservative update: show the higher of current attempt score and the manual score
            attempt.score = max(attempt.score or 0.0, instance.score)

        attempt.save()
    except Exception:
        # avoid crashing admin UI on unexpected errors
        return


@receiver(post_save, sender=SpeakingSubmission)
def update_attempt_on_speaking_save(sender, instance, created, **kwargs):
    """When a speaking submission is graded in admin, reflect the score on the related ExamAttempt.

    Uses the same conservative strategy as writing: if the exam is speaking-only, set the score;
    otherwise update to the max of existing and manual score.
    """
    if instance.score is None:
        return

    exam = instance.question.exam
    try:
        attempt = ExamAttempt.objects.filter(user=instance.user, exam=exam).order_by('-created_at').first()
        if not attempt:
            return

        if exam.skill == 'speaking':
            attempt.score = instance.score
        else:
            attempt.score = max(attempt.score or 0.0, instance.score)

        attempt.save()
    except Exception:
        return
