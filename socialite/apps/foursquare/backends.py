import random
import hashlib

from django.contrib.auth.models import User

from socialite.apps.base.oauth.backends import BaseOauthBackend
from socialite.apps.base.oauth.utils import get_unique_username
from socialite.apps.foursquare import helper, models

class FoursquareBackend(BaseOauthBackend):
    def validate_service_type(self, base_url):
        return base_url == helper.oauth_client.base_url

    def get_existing_user(self, access_token):
        unique_id = helper.get_unique_id(access_token)
        try:
            service = models.FoursquareService.objects.get(unique_id=unique_id)
        except models.FoursquareService.DoesNotExist:
            return None
        return service.user

    def register_user(self, access_token):
        try:
            user_info = helper.user_info(access_token)
        except: # TODO: bare except, bad!
            return None

        screen_name = ''.join((user_info['firstname'], user_info['lastname']))
        user = User(username=get_unique_username(screen_name),
                    first_name=user_info['firstname'],
                    last_name=user_info['lastname'],
                    password=hashlib.md5(str(random.random())).hexdigest())
        user.save()
        return user