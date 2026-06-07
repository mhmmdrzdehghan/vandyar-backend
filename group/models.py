from django.db import models
from account.models import User
from project.models import SubProject
# Create your models here.

class Group(models.Model):
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    subproject  = models.ForeignKey(SubProject, on_delete=models.CASCADE, related_name='groups')
    members     = models.ManyToManyField(
        User,
        related_name="groups_member",
        blank=True
    )  


    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_groups"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title