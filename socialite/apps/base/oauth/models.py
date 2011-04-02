from django.contrib.auth.models import User
from django.db import models

class OauthService(models.Model):

    token = models.CharField(max_length=255, blank=True, default='')
    secret = models.CharField(max_length=255, blank=True, default='')
    unique_id = models.CharField(max_length=255, unique=True)
    impersonated_unique_id = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, related_name="%(class)ss")

    class Meta:
        abstract = True

    def _get_access_token(self):
        if self.token and self.secret:
            return {
                'oauth_token': self.token,
                'oauth_token_secret': self.secret,
            }
        else:
            return None

    def _set_access_token(self, access_token):
        token_dict = {}
        token_dict.update(access_token or {})
        self.token = token_dict.get('oauth_token', '')
        self.secret = token_dict.get('oauth_token_secret', '')

    access_token = property(_get_access_token, _set_access_token)

    @property
    def impersonated(self):
        return bool(self.impersonated_unique_id)

    @property
    def authenticated(self):
        return self.access_token is not None

    def __unicode__(self):
        return "%s for id(%s)" % (self.token, self.user_id)