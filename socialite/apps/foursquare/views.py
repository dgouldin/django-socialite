from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext

from socialite.apps.base.oauth import decorators as oauth_decorators

from socialite.apps.foursquare import helper
from socialite.apps.foursquare.models import FoursquareService

mediator = oauth_decorators.OAuthMediator(helper.oauth_client)

@mediator.authorize
def authorize(request, access_token, redirect_to=settings.LOGIN_REDIRECT_URL):
    service, created = FoursquareService.objects.get_or_create(user=request.user, defaults={
        'token': access_token['oauth_token'],
        'secret': access_token['oauth_token_secret'],
        'unique_id': helper.get_unique_id(access_token),
    })
    if created:
        message = "Foursquare account added."
    else:
        message = "This Foursquare account has already been adeed."
    request.user.message_set.create(message=message)
    return HttpResponseRedirect(redirect_to)

@mediator.authenticate
def authenticate(request, access_token, redirect_to=settings.LOGIN_REDIRECT_URL):
    if request.user.is_authenticated():
        service, created = FoursquareService.objects.get_or_create(user=request.user, defaults={
            'token': access_token['oauth_token'],
            'secret': access_token['oauth_token_secret'],
            'unique_id': helper.get_unique_id(access_token),
        })
        return HttpResponseRedirect(redirect_to)
    return HttpResponse('fail!') # TODO: real response
