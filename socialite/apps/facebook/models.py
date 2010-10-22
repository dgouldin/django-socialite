from django.db import models
from socialite.apps.base.oauth20.models import Oauth20Service

class FacebookServiceManager(models.Manager):
    def update_or_create(self, **kwargs):
        obj, created = self.get_or_create(**kwargs)
        if not created and 'defaults' in kwargs:
            for k,v in kwargs['defaults'].iteritems():
                setattr(obj, k, v)
            obj.save()
        return obj, created

class FacebookService(Oauth20Service):
    objects = FacebookServiceManager()
    pass
