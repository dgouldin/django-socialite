from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate as django_authenticate, login as django_login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

import helper
import utils

REQUEST_TOKEN_FORMAT = '%s:request_token'
ACTION_FORMAT = '%s:action'

class OAuthMediator(object):
    def __init__(self, client, redirect_field_name=REDIRECT_FIELD_NAME):
        self.client = client
        self.view_functions = {}
        self.redirect_field_name = redirect_field_name

    def _redirect(self, request, action):
        callback_url = request.build_absolute_uri(reverse(self.callback))
        request_token = self.client.request_token()
        request.session.update({
            REQUEST_TOKEN_FORMAT % self.client.base_url: request_token,
            ACTION_FORMAT % self.client.base_url: action,
        })
        redirect_url = self.client.get_url(action, token=request_token, callback_url=callback_url)
        return HttpResponseRedirect(redirect_url)

    def callback(self, request):
        request_token = request.session.get(REQUEST_TOKEN_FORMAT % self.client.base_url)
        action = request.session.get(ACTION_FORMAT % self.client.base_url)
        view_function = self.view_functions.get(action)
        if not (request_token and view_function):
            raise Exception("OAuth callback was not able to retrieve the needed information from the session.")
        oauth_verifier = request.GET.get('oauth_verifier')
        access_token = self.client.access_token(request_token, verifier=oauth_verifier)
        if not request.user.is_authenticated():
            user = django_authenticate(client=self.client, access_token=access_token)
            if user:
                django_login(request, user)
        redirect_to = request.session.get('redirect_to') or settings.LOGIN_REDIRECT_URL
        return view_function(request, access_token, redirect_to)

    def authorize(self, view_function):
        self.view_functions[helper.AUTHORIZE] = view_function
        @login_required
        def _authorize(request):
            return self._redirect(request, helper.AUTHORIZE)
        return _authorize

    def authenticate(self, view_function):
        self.view_functions[helper.AUTHENTICATE] = view_function
        def _authenticate(request):
            redirect_to = request.REQUEST.get(self.redirect_field_name, '')
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            if request.user.is_authenticated():
                return HttpResponseRedirect(redirect_to)
            request.session['redirect_to'] = redirect_to
            return self._redirect(request, helper.AUTHENTICATE)
        return _authenticate
