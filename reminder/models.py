from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255,blank=True)
    date = models.DateField()
    time = models.TimeField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='tasks',null=True,blank=True)


class EmailOTP(models.Model):
    email = models.EmailField()
    otp_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.email