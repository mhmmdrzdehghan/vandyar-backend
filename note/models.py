from django.db import models
from account.models import User
from task.models import Task


class Note(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    is_task = models.BooleanField(null=True , blank=True)

    task = models.ForeignKey(Task, on_delete=models.SET_NULL , null=True , blank=True)


    title = models.CharField(max_length=255)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title