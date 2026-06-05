from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Role(models.TextChoices):
    OWNER = "owner", "Owner"
    USER = "user", "User"


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("نام کاربری باید وارد شود")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username



class Profile(models.Model):
    user              = models.OneToOneField(User , related_name='Profile' , on_delete=models.CASCADE)
    phone             = models.CharField(max_length=20, unique=True)
    first_name        = models.CharField( max_length=255)
    last_name         = models.CharField( max_length=255)
    avatar            = models.ImageField(upload_to="avatars/",null=True,blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)
        
