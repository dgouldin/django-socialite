from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext

from socialite.apps.base.oauth20 import decorators as oauth_decorators

from socialite.apps.facebook import helper
from socialite.apps.facebook.models import FacebookService

SCOPES = [
    'publish_stream',
    'offline_access',
]
EXTRA_PARAMS = {'scope': ','.join(SCOPES)}

mediator = oauth_decorators.OAuth20Mediator(helper.oauth_client, params=EXTRA_PARAMS)

@mediator.authorize
def authorize(request, access_token, redirect_to=settings.LOGIN_REDIRECT_URL):
    service, created = FacebookService.objects.update_or_create(user=request.user, defaults={
        'access_token': access_token,
        'unique_id': helper.get_unique_id(access_token),
    })
    if created:
        message = "Facebook account added."
    else:
        message = "This Facebook account has already been adeed."
    request.user.message_set.create(message=message)
    return HttpResponseRedirect(redirect_to)

@mediator.authenticate
def authenticate(request, access_token, redirect_to=settings.LOGIN_REDIRECT_URL):
    if request.user.is_authenticated():
        service, created = FacebookService.objects.update_or_create(user=request.user, defaults={
            'access_token': access_token,
            'unique_id': helper.get_unique_id(access_token),
        })
        return HttpResponseRedirect(redirect_to)
    return HttpResponse('fail!') # TODO: real response
