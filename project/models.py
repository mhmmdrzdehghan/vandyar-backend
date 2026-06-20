
from django.db import models
from account.models import User

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/project", null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_projects"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    



class SubProject(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="subprojects"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    avatar = models.ImageField(upload_to="avatars/subproject", null=True, blank=True)

    status = models.ForeignKey(
        'task.Status',
        on_delete=models.PROTECT,
        related_name="subprojects"
    )


    managers = models.ManyToManyField(
        User,
        related_name="managed_subprojects",
        blank=True
    )

    members = models.ManyToManyField(
        User,
        related_name="subproject_memberships",
        blank=True
        )   

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_subprojects"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.title} - {self.title}"
