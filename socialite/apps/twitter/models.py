from django.db import models
from socialite.apps.base.oauth.models import OauthService

class TwitterServiceManager(models.Manager):
    def update_or_create(self, **kwargs):
        obj, created = self.get_or_create(**kwargs)
        if not created and 'defaults' in kwargs:
            for k,v in kwargs['defaults'].iteritems():
                setattr(obj, k, v)
            obj.save()
        return obj, created

class TwitterService(OauthService):
    objects = TwitterServiceManager()
