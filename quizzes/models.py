from django.db import models

from users.models import User

class Quiz(models.Model):
    title = models.CharField(max_length = 50)
    summary = models.TextField()
    max_solving_time_mins = models.IntegerField()
    is_active = models.BooleanField(default = False)
    is_public = models.BooleanField(default = False)
    is_scheduled = models.BooleanField(default = False)
    starts_at = models.DateTimeField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add = True)
    creator = models.ForeignKey(User, on_delete = models.CASCADE)

    class Meta:
        db_table = 'quiz'

class Question(models.Model):
    title = models.CharField(max_length = 250)
    description = models.TextField()
    score = models.IntegerField(default = 0)
    quiz = models.ForeignKey(Quiz, on_delete = models.CASCADE)

    class Meta:
        db_table = 'question'

class Option(models.Model):
    label = models.CharField(max_length = 100)
    is_correct = models.BooleanField(default = False)
    feedback_message = models.CharField(max_length = 250)
    question = models.ForeignKey(Question, on_delete = models.CASCADE)

    class Meta:
        db_table = 'quiz_option'