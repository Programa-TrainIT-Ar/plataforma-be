from django.db import models
from django.contrib.auth.models import AbstractUser



class Users(AbstractUser):
    is_admin = models.BooleanField(default=False)
    date_birth = models.DateField(null= True, blank = True)

    def __str__(self):
        return self.username



