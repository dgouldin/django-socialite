import urllib

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def twitter_login_required(func):
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated():
            redirect_url = reverse('twitter_authenticate')
            return HttpResponseRedirect('%s?%s' % (redirect_url, urllib.urlencode({
                'next': request.get_full_path(),
            })))
        return func(request, *args, **kwargs)
    return inner
