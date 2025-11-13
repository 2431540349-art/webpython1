from django.db import models
from django.contrib.auth.models import User

class Schedule(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        
    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.date} {self.start_time}"