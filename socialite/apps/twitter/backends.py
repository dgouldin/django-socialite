import random
import hashlib

from django.contrib.auth.models import User

from socialite.apps.base.oauth.backends import BaseOauthBackend
from socialite.apps.base.oauth.utils import get_unique_username
from socialite.apps.twitter import helper, models

class TwitterBackend(BaseOauthBackend):
    def validate_service_type(self, base_url):
        return base_url == helper.oauth_client.base_url

    def populate_user(self, user_info, user=None):
        username = get_unique_username(user_info['screen_name'])
        if not user:
            user = User(username=username, password=hashlib.md5(str(random.random())).hexdigest())
        else:
            user.username = username

        name_parts = user_info['name'].split(' ')
        if len(name_parts) > 1:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
        else:
            first_name, last_name = user_info['name'], ''
        user.first_name = first_name
        user.last_name = last_name
        return user

    def get_existing_user(self, access_token, impersonate=None):
        unique_id = helper.get_unique_id(access_token)
        try:
            service = models.TwitterService.objects.get(unique_id=unique_id)
        except models.TwitterService.DoesNotExist:
            return None

        # update the user record with the newly impersonated user's info
        if service.impersonated_unique_id and service.impersonated_unique_id != impersonate:
            user_info = helper.user_info(access_token, user_id=impersonate)
            user = self.populate_user(user_info, user=service.user)
            user.save()
            self.post_update_user(user, user_info)
        return service.user

    def post_update_user(self, user, user_info):
        pass # hook for subclasses

    def register_user(self, access_token, impersonate=None):
        try:
            user_info = helper.user_info(access_token, user_id=impersonate)
        except Exception,e: # TODO: bare except, bad!
            return None

        user = self.populate_user(user_info)
        user.save()
        self.post_update_user(user, user_info)
        return user