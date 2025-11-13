from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Course, Lesson, Question, Choice, Enrollment

class Command(BaseCommand):
    help = 'Create sample course, lessons, questions and a sample student'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username='sample_student', defaults={'email': 'sample@student.local'})
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created user sample_student (password: password123)'))
        else:
            self.stdout.write('User sample_student already exists')

        course, created = Course.objects.get_or_create(title='Sample Course', defaults={'description': 'This is a sample course for testing.'})
        if created:
            self.stdout.write(self.style.SUCCESS('Created course Sample Course'))
        else:
            self.stdout.write('Course Sample Course already exists')

        lessons_data = [
            ('Introduction', 'This is the introduction lesson with some HTML content. <p>Welcome!</p>'),
            ('Basics', 'Basics of the subject, with examples and explanations.'),
            ('Final Quiz', 'Final lesson that contains the quiz for the course.')
        ]

        lessons = []
        for idx, (ltitle, ldesc) in enumerate(lessons_data, start=1):
            lesson, lcreated = Lesson.objects.get_or_create(course=course, order=idx, defaults={'title': ltitle, 'description': ldesc})
            lessons.append(lesson)
            if lcreated:
                self.stdout.write(self.style.SUCCESS(f'Created lesson: {ltitle}'))
            else:
                self.stdout.write(f'Lesson {ltitle} already exists')

        # Create questions and choices
        for lesson in lessons:
            for qidx in range(1, 3):
                qtext = f'Sample question {qidx} for {lesson.title}?'
                question, qcreated = Question.objects.get_or_create(lesson=lesson, order=qidx, defaults={'question_text': qtext})
                if qcreated:
                    self.stdout.write(self.style.SUCCESS(f'  Created question: {qtext}'))
                else:
                    self.stdout.write(f'  Question already exists: {qtext}')

                # create 4 choices, first one correct
                choices_texts = [
                    f'Correct answer for question {qidx}',
                    f'Wrong answer 1 for question {qidx}',
                    f'Wrong answer 2 for question {qidx}',
                    f'Wrong answer 3 for question {qidx}',
                ]
                for cidx, ctext in enumerate(choices_texts, start=1):
                    is_correct = (cidx == 1)
                    choice, ccreated = Choice.objects.get_or_create(question=question, choice_text=ctext, defaults={'is_correct': is_correct})
                    if ccreated:
                        self.stdout.write(f'    Created choice: {ctext} (correct={is_correct})')

        # Enroll sample student
        Enrollment.objects.get_or_create(user=user, course=course)
        self.stdout.write(self.style.SUCCESS('Enrolled sample_student in Sample Course'))

        self.stdout.write(self.style.SUCCESS('Sample data creation completed.'))
