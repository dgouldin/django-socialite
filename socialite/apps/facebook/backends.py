import random
import hashlib

from django.contrib.auth.models import User

from socialite.apps.base.oauth20.backends import BaseOauthBackend
from socialite.apps.base.oauth20.utils import get_unique_username
from socialite.apps.facebook import helper, models

class FacebookBackend(BaseOauthBackend):
    def validate_service_type(self, base_url):
        return base_url == helper.oauth_client.oauth_base_url

    def get_existing_user(self, access_token):
        unique_id = helper.get_unique_id(access_token)
        try:
            service = models.FacebookService.objects.get(unique_id=unique_id)
        except models.FacebookService.DoesNotExist:
            return None
        return service.user

    def register_user(self, access_token):
        try:
            user_info = helper.user_info(access_token)
        except: # TODO: bare except, bad!
            return None

        screen_name = ''.join((user_info['first_name'], user_info['last_name']))
        user = User(username=get_unique_username(screen_name),
                    first_name=user_info['first_name'],
                    last_name=user_info['last_name'],
                    password=hashlib.md5(str(random.random())).hexdigest())
        user.save()
        return user