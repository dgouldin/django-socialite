import urlparse

from django.conf import settings
from django.contrib.auth.models import User
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

def user_info(access_token, user_id=None):
    if user_id is None:
        url = urlparse.urljoin(api_url, 'account/verify_credentials.json')
    else:
        url = urlparse.urljoin(api_url, 'users/show.json')
        q = get_mutable_query_dict({
            'user_id': user_id,
        })
        url = '%s?%s' % (url, q.urlencode())
    info = simplejson.loads(oauth_client.request(url, access_token))
    return info

def users_info(access_token, user_ids):
    url = urlparse.urljoin(api_url, 'users/lookup.json')
    q = get_mutable_query_dict({
        'user_id': ','.join([str(i) for i in user_ids]),
    })
    url = '%s?%s' % (url, q.urlencode())
    info = simplejson.loads(oauth_client.request(url, access_token))
    return info

def get_unique_id(access_token, user_id=None):
    try:
        return access_token['user_id']
    except KeyError:
        pass
    return user_info(access_token, user_id=user_id)['id']

def get_friend_ids(access_token, user_id=None):
    url = urlparse.urljoin(api_url, 'friends/ids.json')
    if user_id is not None:
        q = get_mutable_query_dict({
            'user_id': user_id,
        })
        url = '%s?%s' % (url, q.urlencode())
    info = simplejson.loads(oauth_client.request(url, access_token))
    return info

def get_follower_ids(access_token, user_id=None):
    url = urlparse.urljoin(api_url, 'followers/ids.json')
    if user_id is not None:
        q = get_mutable_query_dict({
            'user_id': user_id,
        })
        url = '%s?%s' % (url, q.urlencode())
    info = simplejson.loads(oauth_client.request(url, access_token))
    return info

def find_friends(access_token, user_id=None):
    twitter_ids = get_friend_ids(access_token, user_id=None)
    friends = []
    if twitter_ids:
        friends = models.TwitterService.objects.filter(unique_id__in=twitter_ids)
    return friends

def friend_tweets(access_token):
    url = urlparse.urljoin(api_url, 'statuses/friends_timeline.json?count=200')
    return simplejson.loads(oauth_client.request(url, access_token))

AVATAR_SIZES = set(["mini", "normal", "bigger", "reasonably_small"])
def pick_avatar_size(avatar_url, size):
    if not size in AVATAR_SIZES:
        raise ValueError("size must be one of %s" % AVATAR_SIZES)
    avatar_pieces = avatar_url.split('_')
    for possible_size in AVATAR_SIZES:
        if possible_size == size:
            continue
        avatar_pieces[-1] = avatar_pieces[-1].replace(possible_size, size)
    return "_".join(avatar_pieces)

def announce(access_token, message):
    url = urlparse.urljoin(api_url, 'statuses/update.json')
    q = get_mutable_query_dict({'status': message})
    return simplejson.loads(oauth_client.request(url, access_token, method="POST", body=q.urlencode()))

def dm(access_token, user_id, message):
    url = urlparse.urljoin(api_url, 'direct_messages/new.json')
    q = get_mutable_query_dict({
        'user_id': user_id,
        'text': message,
    })
    return simplejson.loads(oauth_client.request(url, access_token, method="POST", body=q.urlencode()))

def get_relationship(access_token, target_user_id, user_id=None):
    url = urlparse.urljoin(api_url, 'friendships/show.json')
    params = {
        'target_id': target_user_id,
    }
    if user_id is not None:
        params['source_id'] = user_id
    q = get_mutable_query_dict(params)
    url = '%s?%s' % (url, q.urlencode())
    return simplejson.loads(oauth_client.request(url, access_token, method="GET"))
