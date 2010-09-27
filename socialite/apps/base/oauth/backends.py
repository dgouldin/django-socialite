from django.contrib.auth.models import User

class BaseOauthBackend:
    def validate_service_type(self, base_url):
        raise NotImplemented

    def get_existing_user(self, access_token):
        raise NotImplemented

    def register_user(self, access_token):
        raise NotImplemented

    def authenticate(self, client=None, access_token=None):
        if client is None or access_token is None or not self.validate_service_type(getattr(client, 'base_url', None)):
            return None
        user = self.get_existing_user(access_token)
        if user:
            return user
        user = self.register_user(access_token)
        return user

    def get_user(self, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None
