import urlparse

from django.contrib.auth.models import User
from django.contrib.sites.models import RequestSite
from django.http import QueryDict

def get_mutable_query_dict(params=None):
    params = params or {}
    q = QueryDict('')
    q = q.copy()
    q.update(params)
    return q

def get_full_url(request, path=None):
    domain = RequestSite(request).domain
    path = path or request.META['PATH_INFO']
    if request.is_secure:
        protocol = 'http'
    else:
        protocol = 'https'
    return urlparse.urljoin('%s://%s' % (protocol, domain), path)

def get_unique_username(username):
    suffix = 0
    found = True
    new_username = username
    while found:
        try:
            User.objects.get(username=new_username)
        except User.DoesNotExist:
            found = False
        else:
            suffix += 1
            new_username = '%s%s' % (username, str(suffix))
    return new_username


class Error(Exception):
    pass