from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, organization, phone, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            organization=organization,
            phone=phone,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, organization, phone, password=None):
        user = self.create_user(
            email,
            name=name,
            organization=organization,
            phone=phone,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'organization', 'phone']

    def __str__(self):
        return self.email