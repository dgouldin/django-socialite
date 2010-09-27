from django.contrib.auth.models import User
from django.db import models

class Oauth20Service(models.Model):

    access_token = models.CharField(max_length=255, unique=True)
    unique_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, related_name="%(class)ss")

    class Meta:
        abstract = True
