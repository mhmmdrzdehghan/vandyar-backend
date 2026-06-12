from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class Notification(models.Model):

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True
    )


    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)

    # optional reference object (task, project, etc)
    object_id = models.IntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["-created_at"]