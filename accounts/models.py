from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')
    full_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    enrolled_users = models.ManyToManyField(User, through='Enrollment', related_name='enrolled_courses')

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Optional short video for the lesson (uploaded file)
    video = models.FileField(upload_to='lesson_videos/', null=True, blank=True)
    order = models.IntegerField(default=0)  # Thứ tự bài học
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500)
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)
    order = models.IntegerField(default=0)  # Thứ tự câu hỏi

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'course']

class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lesson']


class MockExam(models.Model):
    EXAM_TYPES = (
        ('ielts', 'IELTS'),
        ('toeic', 'TOEIC'),
    )
    SKILLS = (
        ('listening', 'Nghe'),
        ('speaking', 'Nói'),
        ('reading', 'Đọc'),
        ('writing', 'Viết'),
    )
    LANGUAGES = (
        ('en-US', 'English (US)'),
        ('en-GB', 'English (UK)'),
        ('en-AU', 'English (Australia)'),
    )

    title = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    skill = models.CharField(max_length=20, choices=SKILLS)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Cấu hình chấm điểm
    auto_weight = models.FloatField(default=0.7, help_text='Trọng số chấm tự động (0.0 - 1.0)')
    manual_weight = models.FloatField(default=0.3, help_text='Trọng số chấm tay (0.0 - 1.0)') 
    speech_language = models.CharField(max_length=10, choices=LANGUAGES, default='en-US',
                                    help_text='Ngôn ngữ sử dụng cho nhận dạng giọng nói')

    def __str__(self):
        return f"{self.get_exam_type_display()} - {self.get_skill_display()} - {self.title}"


class MockQuestion(models.Model):
    exam = models.ForeignKey(MockExam, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    order = models.IntegerField(default=0)
    media_file = models.FileField(upload_to='mock_media/', null=True, blank=True)
    # Optional sample answer text for speaking questions (used by Web Speech API comparison)
    sample_answer = models.TextField(null=True, blank=True, help_text='Sample answer text for speaking questions')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class MockChoice(models.Model):
    question = models.ForeignKey(MockQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class ExamAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(MockExam, on_delete=models.CASCADE)
    score = models.FloatField()
    max_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam} - {self.score}/{self.max_score}"


class SpeakingSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(MockQuestion, on_delete=models.CASCADE)
    audio = models.FileField(upload_to='speaking_submissions/')
    reviewed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Speaking {self.user.username} - {self.question.id}"


class WritingSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(MockQuestion, on_delete=models.CASCADE)
    text = models.TextField()
    reviewed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Writing {self.user.username} - {self.question.id}"


class SentEmail(models.Model):
    """Log mỗi email đã gửi để admin có thể xem lịch sử gửi."""
    to_email = models.CharField(max_length=320)
    subject = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='sent')

    def __str__(self):
        return f"{self.to_email} - {self.subject} @ {self.sent_at:%Y-%m-%d %H:%M}"

    class Meta:
        verbose_name = 'Sent Email'
        verbose_name_plural = 'Sent Emails'