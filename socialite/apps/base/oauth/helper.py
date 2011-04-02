import oauth2 as oauth
import urllib
import urlparse

if not hasattr(urlparse,'parse_qsl'):
    import cgi
    urlparse.parse_qsl = cgi.parse_qsl

REQUEST_TOKEN, AUTHORIZE, AUTHENTICATE, ACCESS_TOKEN = range(4)
OAUTH_ACTIONS = {
    REQUEST_TOKEN: 'request_token',
    AUTHORIZE: 'authorize',
    AUTHENTICATE: 'authenticate',
    ACCESS_TOKEN: 'access_token',
}

class Client:

    def __init__(self, key, secret, base_url, actions=OAUTH_ACTIONS, force_auth_header=False,
        signature_method=None):

        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.actions = actions
        unimplemented = set(OAUTH_ACTIONS.keys()) - set(actions.keys())
        if unimplemented:
            raise Exception("Missing OAuth actions: %s" % ', '.join(OAUTH_ACTIONS[u] for u in unimplemented))
        self.force_auth_header = force_auth_header
        self.signature_method = signature_method

    def get_url(self, action, token=None, callback_url=None):
        try:
            url = urlparse.urljoin(self.base_url, self.actions[action])
        except KeyError:
            raise Exception("Invalid OAuth action.")

        if token:
            if self.signature_method:
                consumer = oauth.Consumer(self.key, self.secret)
                oauth_request = oauth.Request.from_token_and_callback(
                    token=token, callback=callback_url, http_url=url
                )
                oauth_request.sign_request(self.signature_method, consumer, consumer)
                url = oauth_request.to_url()
            else:
                url = '%s?%s' % (url, urllib.urlencode({
                    'oauth_token': token.key,
                }))
        return url

    def request_token(self):
        consumer = oauth.Consumer(self.key, self.secret)
        client = oauth.Client(consumer)
        request_token_url = self.get_url(REQUEST_TOKEN)
        resp, content = client.request(request_token_url)
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        return oauth.Token.from_string(content)

    def access_token(self, request_token, verifier=None):
        consumer = oauth.Consumer(self.key, self.secret)
        client = oauth.Client(consumer, request_token)

        access_token_url = self.get_url(ACCESS_TOKEN)

        if verifier:
            body = "oauth_verifier=%s" % verifier
        else:
            body = None
        resp, content = client.request(access_token_url, method="POST", body=body)
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        return dict(urlparse.parse_qsl(content))

    def request(self, url, access_token, method="GET", body=''):
        consumer = oauth.Consumer(self.key, self.secret)
        token = oauth.Token(key=access_token['oauth_token'], secret=access_token['oauth_token_secret'])
        client = oauth.Client(consumer, token=token)
        resp, content = client.request(url, method=method, body=body)
        if resp['status'] != '200':
            raise Exception("Invalid response %s.\r\n%s" % (resp['status'], content))
        return content
