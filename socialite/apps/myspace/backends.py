import random
import hashlib

from django.contrib.auth.models import User

from socialite.apps.base.oauth.backends import BaseOauthBackend
from socialite.apps.base.oauth.utils import get_unique_username
from socialite.apps.myspace import helper, models

class MyspaceBackend(BaseOauthBackend):
    def validate_service_type(self, base_url):
        return base_url == helper.oauth_client.base_url

    def get_existing_user(self, access_token):
        unique_id = helper.get_unique_id(access_token)
        try:
            service = models.MyspaceService.objects.get(unique_id=unique_id)
        except models.MyspaceService.DoesNotExist:
            return None
        return service.user

    def register_user(self, access_token):
        try:
            user_info = helper.user_info(access_token)
        except: # TODO: bare except, bad!
            return None

        name_parts = user_info['name'].split(' ')
        if len(name_parts) > 1:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
        else:
            first_name, last_name = user_info['name'], ''
        screen_name = user_info['webUri'].split('/')[-1]
        user = User(username=get_unique_username(screen_name),
                    first_name=first_name,
                    last_name=last_name,
                    password=hashlib.md5(str(random.random())).hexdigest())
        user.save()
        return user