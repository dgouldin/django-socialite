from django.contrib.auth.models import User
from django.db import models

class OauthService(models.Model):

    token = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, related_name="%(class)ss")

    class Meta:
        abstract = True
        unique_together = (("token", "secret"),)

    @property
    def access_token(self):
        return {
            'oauth_token': self.token,
            'oauth_token_secret': self.secret,
        }

    def __unicode__(self):
        return "%s for id(%s)" % (self.token, self.user_id)