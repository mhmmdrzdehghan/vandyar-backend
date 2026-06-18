from django.db import models
from account.models import User

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()

    recipients = models.ManyToManyField(
        User,
        related_name="announcements",
        blank=True
    )
    is_active = models.BooleanField(default=True)

    deadline = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title