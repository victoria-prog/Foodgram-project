from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('-id',)

    def __str__(self):
        return self.username
