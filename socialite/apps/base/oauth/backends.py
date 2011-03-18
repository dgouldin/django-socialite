from django.contrib.auth.models import User

class BaseOauthBackend:
    def validate_service_type(self, base_url):
        raise NotImplemented

    def get_existing_user(self, access_token):
        raise NotImplemented

    def register_user(self, access_token):
        """
        # FIXME: Would be good to document that if you want a UserProfile created for OAuth-created users,
           you'll want to hook the post_save signal for User.
        """
        raise NotImplemented

    def authenticate(self, client=None, access_token=None, impersonate=None):
        if client is None or access_token is None or not self.validate_service_type(getattr(client, 'base_url', None)):
            return None
        user = self.get_existing_user(access_token, impersonate=impersonate)
        if user:
            return user
        import logging
        logging.error("FIXME: need to put service prefix on user names to make it clearer which service a user was created for.")
        user = self.register_user(access_token, impersonate=impersonate)
        return user

    def get_user(self, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None
