from django.db import models
from django.db import models
from account.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from project.models import SubProject
from group.models import Group

class Status(models.Model):
    title      = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    
class Priority(models.TextChoices):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

class Task(models.Model):

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True
    )

    title       = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    priority    = models.CharField(max_length=10,choices=Priority.choices,default=Priority.MEDIUM)
    is_routine  = models.BooleanField()
    
    planned_start_at = models.DateTimeField(
        null=True,
        blank=True
    )

    deadline = models.DateTimeField(
        null=True,
        blank=True
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_tasks"
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="task_assignments"
    )

    start_time = models.DateTimeField(
        null=True,
        blank=True
    )

    end_time = models.DateTimeField(
        null=True,
        blank=True
    )

    forwarded_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="forwarded_tasks"
    )

    quality_rate = models.IntegerField(
        null=True,
        blank=True,
        validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ]
    )

    parent_id = models.ForeignKey(
    "self",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="forwarded_tasks"
    )

    root_task = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_chain"
    )

    can_forward = models.BooleanField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        blank=True,
        null=True,
    )
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TaskRoutine(models.Model):

    class Period(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name="routine"
    )

    period = models.CharField(
        max_length=20,
        choices=Period.choices
    )

    start_date = models.DateTimeField()

    end_date = models.DateTimeField(
        null=True,
        blank=True
    )

    next_run_at = models.DateTimeField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )    


class TaskAttachment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(
        upload_to="tasks/attachments/%Y/%m/%d/"
    )

    file_name = models.CharField(
        max_length=255
    )

    file_path = models.TextField()

    file_size = models.BigIntegerField()

    file_type = models.CharField(
        max_length=100,
        blank=True
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_task_attachments"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.file_name

class CheckList(models.Model):
    task  = models.ForeignKey(Task, on_delete=models.CASCADE , related_name='check_lists')  
    title = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

