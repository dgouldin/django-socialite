import httplib2
import urllib
import sys
try:
    from urlparse import parse_qs, parse_qsl, urljoin
except ImportError:
    from urlparse import urljoin
    from cgi import parse_qs, parse_qsl

REQUEST_TOKEN, AUTHORIZE, AUTHENTICATE, ACCESS_TOKEN = 0, 1, 2, 3

class Client(object):
    """Client for OAuth 2.0 draft spec
    https://svn.tools.ietf.org/html/draft-hammer-oauth2-00
    """

    def __init__(self, client_id, client_secret, oauth_base_url,
        redirect_uri=None, cache=None, timeout=None, proxy_info=None):

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.oauth_base_url = oauth_base_url

        if self.client_id is None or self.client_secret is None or \
           self.oauth_base_url is None:
            raise ValueError("Client_id and client_secret must be set.")

        http_kwargs = dict(cache=cache, 
                           timeout=timeout,
                           proxy_info=proxy_info)
        if sys.version.startswith("2.5"):
            http_kwargs['disable_ssl_certificate_validation'] = True
        self.http = httplib2.Http(**http_kwargs)

    @staticmethod
    def _split_url_string(param_str):
        """Turn URL string into parameters."""
        parameters = parse_qs(param_str, keep_blank_values=False)
        for key, val in parameters.iteritems():
            parameters[key] = urllib.unquote(val[0])
        return parameters

    def authorization_url(self, redirect_uri=None, params=None, state=None,
        immediate=None, endpoint='authorize'):
        """Get the URL to redirect the user for client authorization
        https://svn.tools.ietf.org/html/draft-hammer-oauth2-00#section-3.5.2.1
        """

        # prepare required args
        args = {
            'type': 'web_server',
            'client_id': self.client_id,
        }

        # prepare optional args
        redirect_uri = redirect_uri or self.redirect_uri
        if redirect_uri is not None:
            args['redirect_uri'] = redirect_uri
        if state is not None:
            args['state'] = state
        if immediate is not None:
            args['immediate'] = str(immediate).lower()

        args.update(params or {})

        return '%s?%s' % (urljoin(self.oauth_base_url, endpoint),
            urllib.urlencode(args))

    def access_token(self, code, redirect_uri, secret_type=None,
        endpoint='access_token'):
        """Get an access token from the supplied code
        https://svn.tools.ietf.org/html/draft-hammer-oauth2-00#section-3.5.2.2
        """

        # prepare required args
        if code is None:
            raise ValueError("Code must be set.")
        if redirect_uri is None:
            raise ValueError("Redirect_uri must be set.")
        args = {
            'type': 'web_server',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
        }

        # prepare optional args
        if secret_type is not None:
            args['secret_type'] = secret_type

        uri = urljoin(self.oauth_base_url, endpoint)
        body = urllib.urlencode(args)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response, content = self.http.request(uri, method='POST', body=body,
            headers=headers)
        if not response.status == 200:
            raise Error(content)
        response_args = Client._split_url_string(content)

        error = response_args.pop('error', None)
        if error is not None:
            raise Error(error)

        refresh_token = response_args.pop('refresh_token', None)
        if refresh_token is not None:
            response_args = self.refresh(refresh_token, secret_type=secret_type)
        return response_args

    def refresh(self, refresh_token, secret_type=None, endpoint='access_token'):
        """Get a new access token from the supplied refresh token
        https://svn.tools.ietf.org/html/draft-hammer-oauth2-00#section-4
        """

        if refresh_token is None:
            raise ValueError("Refresh_token must be set.")

        # prepare required args
        args = {
            'type': 'refresh',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
        }

        # prepare optional args
        if secret_type is not None:
            args['secret_type'] = secret_type

        uri = urljoin(self.oauth_base_url, endpoint)
        body = urllib.urlencode(args)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response, content = self.http.request(uri, method='POST', body=body,
            headers=headers)
        if not response.status == 200:
            raise Error(content)

        response_args = Client._split_url_string(content)
        return response_args

    def request(self, base_uri, access_token=None, method='GET', body=None,
        headers=None, params=None, token_param='oauth_token'):
        """Make a request to the OAuth API"""

        args = {}
        args.update(params or {})
        if access_token is not None and method == 'GET':
            args[token_param] = access_token
        uri = '%s?%s' % (base_uri, urllib.urlencode(args))
        return self.http.request(uri, method=method, body=body, headers=headers)
