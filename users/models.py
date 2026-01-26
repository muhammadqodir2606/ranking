from django.contrib.auth.models import AbstractUser
from django.db import models

from shared.models import BaseModel


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
