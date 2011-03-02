import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import simplejson

from socialite.apps.base.oauth import helper as oauth_helper
from socialite.apps.base.oauth.utils import get_mutable_query_dict
from socialite.apps.twitter import models

api_url = 'http://api.twitter.com/1/'
oauth_url = 'http://twitter.com/oauth/'
oauth_actions = {
    oauth_helper.REQUEST_TOKEN: 'request_token',
    oauth_helper.AUTHORIZE: 'authorize',
    oauth_helper.AUTHENTICATE: 'authenticate',
    oauth_helper.ACCESS_TOKEN: 'access_token',
}
oauth_client = oauth_helper.Client(settings.TWITTER_KEY, settings.TWITTER_SECRET, oauth_url, oauth_actions)

def user_info(access_token):
    CACHE_KEY = 'twitter:user_info:%s:' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        url = urlparse.urljoin(api_url, 'account/verify_credentials.json')
        info = simplejson.loads(oauth_client.request(url, access_token))
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def users_info(access_token, user_ids):
    CACHE_KEY = 'twitter:users_info:%s:%s' % (access_token, ','.join([str(i) for i in user_ids]))
    info = cache.get(CACHE_KEY)
    if info is None:
        url = urlparse.urljoin(api_url, 'users/lookup.json')
        q = get_mutable_query_dict({
            'user_id': ','.join([str(i) for i in user_ids]),
        })
        url = '%s?%s' % (url, q.urlencode())
        info = simplejson.loads(oauth_client.request(url, access_token))
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def get_unique_id(access_token):
    try:
        return access_token['user_id']
    except KeyError:
        pass
    return user_info(access_token)['id']

def get_friend_ids(access_token):
    CACHE_KEY = 'twitter:get_friend_ids:%s' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        url = urlparse.urljoin(api_url, 'friends/ids.json')
        info = simplejson.loads(oauth_client.request(url, access_token))
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def get_follower_ids(access_token):
    CACHE_KEY = 'twitter:get_friend_ids:%s' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        url = urlparse.urljoin(api_url, 'followers/ids.json')
        info = simplejson.loads(oauth_client.request(url, access_token))
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def find_friends(access_token):
    twitter_ids = get_friend_ids(access_token)
    friends = []
    if twitter_ids:
        friends = models.TwitterService.objects.filter(unique_id__in=twitter_ids)
    return friends

def friend_tweets(access_token):
    url = urlparse.urljoin(api_url, 'statuses/friends_timeline.json?count=200')
    return simplejson.loads(oauth_client.request(url, access_token))

def announce(access_token, message):
    url = urlparse.urljoin(api_url, 'statuses/update.json')
    q = get_mutable_query_dict({'status': message})
    return simplejson.loads(oauth_client.request(url, access_token, method="POST", body=q.urlencode()))
