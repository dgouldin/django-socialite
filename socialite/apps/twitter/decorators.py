import urllib
import urlparse

from django.conf import settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def twitter_login_required(func):
    def inner(request, *args, **kwargs):
        # hack the impersonate paramter out of the querystring before continuing
        params = dict(urlparse.parse_qsl(request.META['QUERY_STRING']))
        impersonate = params.pop(settings.TWITTER_IMPERSONATE_SESSION_KEY, None)

        if impersonate is not None:
            logout(request)

        if not request.user.is_authenticated():
            redirect_url = reverse('twitter_authenticate')

            request.META['QUERY_STRING'] = urllib.urlencode(params)
            if impersonate:
                request.session[settings.TWITTER_IMPERSONATE_SESSION_KEY] = impersonate
            return HttpResponseRedirect('%s?%s' % (redirect_url, urllib.urlencode({
                'next': request.get_full_path(),
            })))
        return func(request, *args, **kwargs)
    return inner
