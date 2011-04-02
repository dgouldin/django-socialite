import random
import hashlib

from django.contrib.auth.models import User

from socialite.apps.base.oauth.utils import get_unique_username
from socialite.apps.twitter import models
from socialite.apps.twitter.signals import post_register_service

def register_service(user_info, unique_id=None, access_token=None, impersonate=None):
    # FIXME: massive race condition potential here
    unique_id = unique_id or user_info['id_str']

    try:
        service = models.TwitterService.objects.get(unique_id=unique_id)
    except models.TwitterService.DoesNotExist:
        user = User(password=hashlib.md5(str(random.random())).hexdigest())
        service = models.TwitterService()
    else:
        user = service.user

    # update user
    user.username = get_unique_username(user_info['screen_name'], user_id=user.id)
    name_parts = user_info['name'].split(' ')
    if len(name_parts) > 1:
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:])
    else:
        first_name, last_name = user_info['name'], ''
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    # update service
    service.user = user
    service.unique_id = unique_id
    service.screen_name = user_info['screen_name']
    service.impersonated_unique_id = impersonate or ''
    service.access_token = access_token
    service.save()
    post_register_service.send(sender=models.TwitterService, instance=service, user_info=user_info)

    return service
