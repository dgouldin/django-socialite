import urllib
import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def twitter_login_required(func):
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated():
            redirect_url = reverse('twitter_authenticate')

            # hack the impersonate paramter out of the querystring before continuing
            params = dict(urlparse.parse_qsl(request.META['QUERY_STRING']))
            impersonate = params.pop(settings.TWITTER_IMPERSONATE_SESSION_KEY, None)
            request.META['QUERY_STRING'] = urllib.urlencode(params)
            if impersonate:
                request.session[settings.TWITTER_IMPERSONATE_SESSION_KEY] = impersonate
            return HttpResponseRedirect('%s?%s' % (redirect_url, urllib.urlencode({
                'next': request.get_full_path(),
            })))
        return func(request, *args, **kwargs)
    return inner
