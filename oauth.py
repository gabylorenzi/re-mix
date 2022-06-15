import base64
import logging
import os
import time
import warnings
import webbrowser

import requests
# Workaround to support both python 2 & 3
import six
import six.moves.urllib.parse as urllibparse
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from six.moves.urllib_parse import parse_qsl, urlparse

from spotipy.cache_handler import CacheFileHandler, CacheHandler
from spotipy.util import CLIENT_CREDS_ENV_VARS, get_host_port, 

def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(
        six.text_type(client_id + ":" + client_secret).encode("ascii")
    )
    return {"Authorization": "Basic %s" % auth_header.decode("ascii")}

def normalize_scope(scope):
    if scope:
        if isinstance(scope, str):
            scopes = scope.split(',')
        elif isinstance(scope, list) or isinstance(scope, tuple):
            scopes = scope
        else:
            raise Exception(
                "Unsupported scope value, please either provide a list of scopes, "
                "or a string of scopes separated by commas"
            )
        return " ".join(sorted(scopes))
    else:
        return None

class SpotifyOAuth(SpotifyAuthBase):
    """
    Implements Authorization Code Flow for Spotify's OAuth implementation.
    """
    OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
            self,
            client_id=None, #pass in 
            client_secret=None, #pass in
            redirect_uri=None, #pass in 
            state=None,
            scope=None, #pass in 
            cache_path=None,
            username=None,
            proxies=None,
            show_dialog=False,
            requests_session=True,
            requests_timeout=None,
            open_browser=True,
            cache_handler=None
    ):
        """
        Creates a SpotifyOAuth object
        Parameters:
             * client_id: Must be supplied or set as environment variable
             * client_secret: Must be supplied or set as environment variable
             * redirect_uri: Must be supplied or set as environment variable
             * state: Optional, no verification is performed
             * scope: Optional, either a list of scopes or comma separated string of scopes.
                      e.g, "playlist-read-private,playlist-read-collaborative"
             * cache_path: (deprecated) Optional, will otherwise be generated
                           (takes precedence over `username`)
             * username: (deprecated) Optional or set as environment variable
                         (will set `cache_path` to `.cache-{username}`)
             * proxies: Optional, proxy for the requests library to route through
             * show_dialog: Optional, interpreted as boolean
             * requests_session: A Requests session
             * requests_timeout: Optional, tell Requests to stop waiting for a response after
                                 a given number of seconds
             * open_browser: Optional, whether or not the web browser should be opened to
                             authorize a user
             * cache_handler: An instance of the `CacheHandler` class to handle
                              getting and saving cached authorization tokens.
                              Optional, will otherwise use `CacheFileHandler`.
                              (takes precedence over `cache_path` and `username`)
        """

        super(SpotifyOAuth, self).__init__(requests_session)

        self.client_id = client_id #pass in 
        self.client_secret = client_secret #pass in 
        self.redirect_uri = redirect_uri #pass in 
        self.state = state
        self.scope = self._normalize_scope(scope) #pass in (added function to this file)
        if username or cache_path:
            warnings.warn("Specifying cache_path or username as arguments to SpotifyOAuth " +
                          "will be deprecated. Instead, please create a CacheFileHandler " +
                          "instance with the desired cache_path and username and pass it " +
                          "to SpotifyOAuth as the cache_handler. For example:\n\n" +
                          "\tfrom spotipy.oauth2 import CacheFileHandler\n" +
                          "\thandler = CacheFileHandler(cache_path=cache_path, " +
                          "username=username)\n" +
                          "\tsp = spotipy.SpotifyOAuth(client_id, client_secret, " +
                          "redirect_uri," +
                          " cache_handler=handler)",
                          DeprecationWarning
                          )
            if cache_handler:
                warnings.warn("A cache_handler has been specified along with a cache_path or " +
                              "username. The cache_path and username arguments will be ignored.")
        if cache_handler:
            assert issubclass(cache_handler.__class__, CacheHandler), \
                "cache_handler must be a subclass of CacheHandler: " + str(type(cache_handler)) \
                + " != " + str(CacheHandler)
            self.cache_handler = cache_handler
        else:
            username = (username or os.getenv(CLIENT_CREDS_ENV_VARS["client_username"]))
            self.cache_handler = CacheFileHandler(
                username=username,
                cache_path=cache_path
            )
        self.proxies = proxies
        self.requests_timeout = requests_timeout
        self.show_dialog = show_dialog
        self.open_browser = open_browser

    def validate_token(self, token_info):
        if token_info is None:
            return None

        # if scopes don't match, then bail
        if "scope" not in token_info or not self._is_scope_subset(
                self.scope, token_info["scope"]
        ):
            return None

        if self.is_token_expired(token_info):
            token_info = self.refresh_access_token(
                token_info["refresh_token"]
            )

        return token_info

    def get_authorize_url(self, state=None):
        """ Gets the URL to use to authorize this app
        """
        payload = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }
        if self.scope:
            payload["scope"] = self.scope
        if state is None:
            state = self.state
        if state is not None:
            payload["state"] = state
        if self.show_dialog:
            payload["show_dialog"] = True

        urlparams = urllibparse.urlencode(payload)

        return "%s?%s" % (self.OAUTH_AUTHORIZE_URL, urlparams)

    def parse_response_code(self, url):
        """ Parse the response code in the given response url
            Parameters:
                - url - the response url
        """
        _, code = self.parse_auth_response_url(url)
        if code is None:
            return url
        else:
            return code

    @staticmethod
    def parse_auth_response_url(url):
        query_s = urlparse(url).query
        form = dict(parse_qsl(query_s))
        if "error" in form:
            raise SpotifyOauthError("Received error from auth server: "
                                    "{}".format(form["error"]),
                                    error=form["error"])
        return tuple(form.get(param) for param in ["state", "code"])

    def _make_authorization_headers(self):
        return _make_authorization_headers(self.client_id, self.client_secret)

    def _open_auth_url(self):
        auth_url = self.get_authorize_url()
        try:
            webbrowser.open(auth_url)
            logger.info("Opened %s in your browser", auth_url)
        except webbrowser.Error:
            logger.error("Please navigate here: %s", auth_url)

    def _get_auth_response_interactive(self, open_browser=False):
        if open_browser:
            self._open_auth_url()
            prompt = "Enter the URL you were redirected to: "
        else:
            url = self.get_authorize_url()
            prompt = (
                "Go to the following URL: {}\n"
                "Enter the URL you were redirected to: ".format(url)
            )
        response = self._get_user_input(prompt)
        state, code = SpotifyOAuth.parse_auth_response_url(response)
        if self.state is not None and self.state != state:
            raise SpotifyStateError(self.state, state)
        return code

    def _get_auth_response_local_server(self, redirect_port):
        server = start_local_http_server(redirect_port)
        self._open_auth_url()
        server.handle_request()

        if server.error is not None:
            raise server.error
        elif self.state is not None and server.state != self.state:
            raise SpotifyStateError(self.state, server.state)
        elif server.auth_code is not None:
            return server.auth_code
        else:
            raise SpotifyOauthError("Server listening on localhost has not been accessed")

    def get_auth_response(self, open_browser=None):
        logger.info('User authentication requires interaction with your '
                    'web browser. Once you enter your credentials and '
                    'give authorization, you will be redirected to '
                    'a url.  Paste that url you were directed to to '
                    'complete the authorization.')

        redirect_info = urlparse(self.redirect_uri)
        redirect_host, redirect_port = get_host_port(redirect_info.netloc)

        if open_browser is None:
            open_browser = self.open_browser

        if (
                open_browser
                and redirect_host in ("127.0.0.1", "localhost")
                and redirect_info.scheme == "http"
        ):
            # Only start a local http server if a port is specified
            if redirect_port:
                return self._get_auth_response_local_server(redirect_port)
            else:
                logger.warning('Using `%s` as redirect URI without a port. '
                               'Specify a port (e.g. `%s:8080`) to allow '
                               'automatic retrieval of authentication code '
                               'instead of having to copy and paste '
                               'the URL your browser is redirected to.',
                               redirect_host, redirect_host)

        return self._get_auth_response_interactive(open_browser=open_browser)

    def get_authorization_code(self, response=None):
        if response:
            return self.parse_response_code(response)
        return self.get_auth_response()

    def get_access_token(self, code=None, as_dict=True, check_cache=True):
        """ Gets the access token for the app given the code
            Parameters:
                - code - the response code
                - as_dict - a boolean indicating if returning the access token
                            as a token_info dictionary, otherwise it will be returned
                            as a string.
        """
        if as_dict:
            warnings.warn(
                "You're using 'as_dict = True'."
                "get_access_token will return the token string directly in future "
                "versions. Please adjust your code accordingly, or use "
                "get_cached_token instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        if check_cache:
            token_info = self.validate_token(self.cache_handler.get_cached_token())
            if token_info is not None:
                if self.is_token_expired(token_info):
                    token_info = self.refresh_access_token(
                        token_info["refresh_token"]
                    )
                return token_info if as_dict else token_info["access_token"]

        payload = {
            "redirect_uri": self.redirect_uri,
            "code": code or self.get_auth_response(),
            "grant_type": "authorization_code",
        }
        if self.scope:
            payload["scope"] = self.scope
        if self.state:
            payload["state"] = self.state

        headers = self._make_authorization_headers()

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL, headers, payload
        )

        try:
            response = self._session.post(
                self.OAUTH_TOKEN_URL,
                data=payload,
                headers=headers,
                verify=True,
                proxies=self.proxies,
                timeout=self.requests_timeout,
            )
            response.raise_for_status()
            token_info = response.json()
            token_info = self._add_custom_values_to_token_info(token_info)
            self.cache_handler.save_token_to_cache(token_info)
            return token_info if as_dict else token_info["access_token"]
        except requests.exceptions.HTTPError as http_error:
            self._handle_oauth_error(http_error)

    def refresh_access_token(self, refresh_token):
        payload = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        headers = self._make_authorization_headers()

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL, headers, payload
        )

        try:
            response = self._session.post(
                self.OAUTH_TOKEN_URL,
                data=payload,
                headers=headers,
                proxies=self.proxies,
                timeout=self.requests_timeout,
            )
            response.raise_for_status()
            token_info = response.json()
            token_info = self._add_custom_values_to_token_info(token_info)
            if "refresh_token" not in token_info:
                token_info["refresh_token"] = refresh_token
            self.cache_handler.save_token_to_cache(token_info)
            return token_info
        except requests.exceptions.HTTPError as http_error:
            self._handle_oauth_error(http_error)

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        token_info["scope"] = self.scope
        return token_info

    def get_cached_token(self):
        warnings.warn("Calling get_cached_token directly on the SpotifyOAuth object will be " +
                      "deprecated. Instead, please specify a CacheFileHandler instance as " +
                      "the cache_handler in SpotifyOAuth and use the CacheFileHandler's " +
                      "get_cached_token method. You can replace:\n\tsp.get_cached_token()" +
                      "\n\nWith:\n\tsp.validate_token(sp.cache_handler.get_cached_token())",
                      DeprecationWarning
                      )
        return self.validate_token(self.cache_handler.get_cached_token())

    def _save_token_info(self, token_info):
        warnings.warn("Calling _save_token_info directly on the SpotifyOAuth object will be " +
                      "deprecated. Instead, please specify a CacheFileHandler instance as " +
                      "the cache_handler in SpotifyOAuth and use the CacheFileHandler's " +
                      "save_token_to_cache method.",
                      DeprecationWarning
                      )
        self.cache_handler.save_token_to_cache(token_info)
        return None