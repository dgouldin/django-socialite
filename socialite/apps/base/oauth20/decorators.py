from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate as django_authenticate, login as django_login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext

import helper
import utils

REQUEST_TOKEN_FORMAT = '%s:request_token'
ACTION_FORMAT = '%s:action'

class OAuth20Mediator(object):
    def __init__(self, client, params=None, redirect_field_name=REDIRECT_FIELD_NAME):
        self.client = client
        self.params = params
        self.redirect_field_name = redirect_field_name
        self.view_functions = {}

    def login(self, request, access_token):
        user = django_authenticate(client=self.client, access_token=access_token)
        if user:
            django_login(request, user)
        return user
    
    def callback(self, request):
        action = request.session.get(ACTION_FORMAT % self.client.oauth_base_url)
        view_function = self.view_functions.get(action)
        if not view_function:
            raise Exception("OAuth callback was not able to retrieve the needed information from the session.")
        
        access_token = request.GET.get('access_token')
        code = request.GET.get('code')
        if code and access_token is None:
            access_token_args = self.client.access_token(code, request.build_absolute_uri(reverse(self.callback)))
            access_token = access_token_args.get('access_token')
        if not access_token:
            t = loader.get_template(access_token_template)
            return HttpResponse(t.render(RequestContext(request, {})))

        if not request.user.is_authenticated():
            user = self.login(request, access_token)
        redirect_to = request.session.get('redirect_to') or settings.LOGIN_REDIRECT_URL
        return view_function(request, access_token, redirect_to)

    def authorize(self, view_function):
        self.view_functions[helper.AUTHORIZE] = view_function
        @login_required
        def _authorize(request):
            request.session[ACTION_FORMAT % self.client.oauth_base_url] = helper.AUTHORIZE
            redirect_uri = request.build_absolute_uri(reverse(self.callback))
            return HttpResponseRedirect(self.client.authorization_url(params=self.params, redirect_uri=redirect_uri))
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
            request.session[ACTION_FORMAT % self.client.oauth_base_url] = helper.AUTHENTICATE
            redirect_uri = request.build_absolute_uri(reverse(self.callback))
            return HttpResponseRedirect(self.client.authorization_url(params=self.params, redirect_uri=redirect_uri))
        return _authenticate
