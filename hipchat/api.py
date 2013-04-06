import requests


class HipchatError(Exception):
    """HipChat API error

    See https://www.hipchat.com/docs/api/response_codes for possible
    errors.

    """

class AuthorizationError(HipchatError):
    """Raised when auth_token is invalid or not adequate for the operation."""


class NotFoundError(HipchatError):
    """Specified room or user not found."""


class RateLimitExceeded(HipchatError):
    """The rate limit has been exceeded."""


class ServiceUnavailable(HipchatError):
    """The service is temporarily unavailably."""


class BadRequest(HipchatError):
    """Error in data provided in the request."""


class Api(object):
    BASE_URL = 'https://api.hipchat.com/v1/'
    FROM_NAME = 'API'

    def __init__(self, auth_token, from_name=None, base_url=None):
        self.auth_token = auth_token
        self.base_url = base_url or self.BASE_URL
        self.from_name = from_name or self.FROM_NAME
        self._room_class = None
        self._user_class = None

    def __repr__(self):
        return '<Api auth_token="%s">' % str(self.auth_token)

    @staticmethod
    def _unwrap_response(resp):
        code = resp.status_code
        json = resp.json()
        errmsg = json.get('error', {}).get('message', 'Unknown error')

        if code == 200:
            return json
        elif code == 400:
            raise BadRequest(errmsg)
        elif code == 401:
            raise AuthorizationError(errmsg)
        elif code == 404:
            raise NotFoundError(errmsg)
        elif code == 403:
            raise RateLimitExceeded(errmsg)
        elif code == 503:
            raise ServiceUnavailable(errmsg)
        else:
            raise HipchatError('%d: %s' % (code, errmsg))

    def _get(self, method, **kwargs):
        url = self.base_url + method
        kwargs.update({
            'format': 'json',
            'auth_token': self.auth_token
        })
        resp = requests.get(url, params=kwargs)
        return self._unwrap_response(resp)

    def _post(self, method, **kwargs):
        url = self.base_url + method
        params = {
            'format': 'json',
            'auth_token': self.auth_token
        }
        kwargs.update({
            'from': self.from_name
        })
        resp = requests.post(url, params=params, data=kwargs)
        return self._unwrap_response(resp)

    @property
    def rooms(self):
        """Rooms"""
        if self._room_class is None:
            from .data import Room
            self._room_class = type('Room', (Room,), dict(api=self))
        return self._room_class

    @property
    def users(self):
        """Users"""
        if self._user_class is None:
            from .data import User
            self._user_class = type('User', (User,), dict(api=self))
        return self._user_class
