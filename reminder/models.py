from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



class EmailOTP(models.Model):
    email = models.EmailField()
    otp_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.email