from socialite.apps.base.oauth.backends import BaseOauthBackend
from socialite.apps.twitter import helper, models
from socialite.apps.twitter.registration import register_service

class TwitterBackend(BaseOauthBackend):
    def validate_service_type(self, base_url):
        return base_url == helper.oauth_client.base_url

    def get_existing_user(self, access_token, impersonate=None):
        unique_id = helper.get_unique_id(access_token)
        try:
            service = models.TwitterService.objects.get(unique_id=unique_id,
                impersonated_unique_id=impersonate or '')
        except models.TwitterService.DoesNotExist:
            return None

    def register_user(self, access_token, impersonate=None):
        try:
            user_info = helper.user_info(access_token, user_id=impersonate)
        except Exception,e: # TODO: bare except, bad!
            return None

        unique_id = helper.get_unique_id(access_token)
        return register_service(user_info, unique_id=unique_id,
            access_token=access_token, impersonate=impersonate).user
