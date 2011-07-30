import oauth2 as oauth
import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import simplejson

from socialite.apps.base.oauth import helper as oauth_helper
from socialite.apps.base.oauth20.utils import get_mutable_query_dict

from socialite.apps.myspace import models

api_url = 'http://api.myspace.com/v1/'
oauth_url = 'http://api.myspace.com/'
oauth_actions = {
    oauth_helper.REQUEST_TOKEN: 'request_token',
    oauth_helper.AUTHORIZE: 'authorize',
    oauth_helper.AUTHENTICATE: 'authorize',
    oauth_helper.ACCESS_TOKEN: 'access_token',
}
oauth_client = oauth_helper.Client(settings.MYSPACE_KEY, settings.MYSPACE_SECRET, oauth_url, oauth_actions,
    signature_method=oauth.SignatureMethod_HMAC_SHA1())

def user_info(access_token):
    CACHE_KEY = 'myspace:user_info:%s:' % access_token
    info = cache.get(CACHE_KEY)
    if info is None:
        url = urlparse.urljoin(api_url, 'user.json')
        info = simplejson.loads(oauth_client.request(url, access_token))
        cache.set(CACHE_KEY, info, 60 * 5) # 5 minutes
    return info

def get_unique_id(access_token):
    return user_info(access_token)['userId']

