import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import simplejson

from socialite.apps.base.oauth import helper as oauth_helper
from socialite.apps.base.oauth.utils import get_mutable_query_dict

from socialite.apps.foursquare import models

api_url = 'http://api.foursquare.com/v1/'
oauth_url = 'http://foursquare.com/oauth/'
oauth_actions = {
    oauth_helper.REQUEST_TOKEN: 'request_token',
    oauth_helper.AUTHORIZE: 'authorize',
    oauth_helper.AUTHENTICATE: 'authorize',
    oauth_helper.ACCESS_TOKEN: 'access_token',
}
oauth_client = oauth_helper.Client(settings.FOURSQUARE_KEY, settings.FOURSQUARE_SECRET, oauth_url, oauth_actions)

def user_info(access_token):
    CACHE_KEY = 'foursquare:user_info:%s:' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        url = urlparse.urljoin(api_url, 'user.json')
        info = simplejson.loads(oauth_client.request(url, access_token)).get('user')
        #cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def get_unique_id(access_token):
    return user_info(access_token)['id']

def get_friend_ids(access_token):
    CACHE_KEY = 'foursquare:get_friend_ids:%s' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        url = urlparse.urljoin(api_url, 'friends.json')
        users = simplejson.loads(oauth_client.request(url, access_token))
        info = [u['id'] for u in users['friends']]
        #cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def find_friends(access_token):
    foursquare_ids = get_friend_ids(access_token)
    friends = []
    if foursquare_ids:
        friends = models.FoursquareService.objects.filter(unique_id__in=foursquare_ids)
    return friends

def announce(access_token, message):
    url = urlparse.urljoin(api_url, 'checkin.json')
    q = get_mutable_query_dict({'shout': message})
    return simplejson.loads(oauth_client.request(url, access_token, method="POST", body=q.urlencode()))
