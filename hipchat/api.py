import requests


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

    def _get(self, method, **kwargs):
        url = self.base_url + method
        kwargs.update({
            'format': 'json',
            'auth_token': self.auth_token
        })
        resp = requests.get(url, params=kwargs)
        return resp.json()

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
        return resp.json()

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
