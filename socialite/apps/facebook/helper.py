import urllib
import urlparse

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils import simplejson

from socialite.apps.base.oauth20 import helper as oauth_helper
from socialite.apps.base.oauth20.utils import get_mutable_query_dict

import models

api_url = 'https://graph.facebook.com/'
oauth_url = 'https://graph.facebook.com/oauth/'
oauth_client = oauth_helper.Client(settings.FACEBOOK_APPLICATION_ID, settings.FACEBOOK_SECRET, oauth_url)

def users_info(access_token, ids):
    CACHE_KEY = 'facebook:users_info:%s:%s' % (access_token, ','.join([str(i) for i in ids]))
    info = cache.get(CACHE_KEY)
    if info is None:
        base_uri = api_url
        fields = [
            'id',
            'name',
            'picture',
        ]
        params = {
            'ids': ','.join([str(i) for i in ids],),
            'fields': ','.join(fields),
        }
        r,c = oauth_client.request(base_uri, access_token=access_token, params=params)
        # TODO: handle response != 200
        info = simplejson.loads(c).values()
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def user_info(access_token):
    CACHE_KEY = 'facebook:user_info:%s' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        base_uri = urlparse.urljoin(api_url, 'me')
        fields = [
            'id',
            'first_name',
            'last_name',
            'name',
            'picture',
        ]
        params = {
            'fields': ','.join(fields),
        }
        r,c = oauth_client.request(base_uri, access_token=access_token, params=params)
        # TODO: handle response != 200
        info = simplejson.loads(c)
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def get_unique_id(access_token):
    info = user_info(access_token)
    return info['id']

def get_friend_ids(access_token):
    CACHE_KEY = 'facebook:get_friend_ids:%s' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        base_uri = urlparse.urljoin(api_url, 'me/friends')
        r,c = oauth_client.request(base_uri, access_token=access_token)
        # TODO: handle response != 200
        friends = simplejson.loads(c)
        info = [f['id'] for f in friends['data']]
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def find_friends(access_token):
    facebook_ids = get_friend_ids(access_token)
    friends = []
    if facebook_ids:
        friends = models.FacebookService.objects.filter(unique_id__in=facebook_ids)
    return friends

def announce(access_token, message):
    base_uri = urlparse.urljoin(api_url, 'me/feed')
    q = get_mutable_query_dict({
        'access_token': access_token,
        'message': message,
    })
    r,c = oauth_client.request(base_uri, access_token=access_token, method="POST", body=q.urlencode())
    # TODO: handle response != 200
    return simplejson.loads(c)
