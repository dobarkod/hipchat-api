"""
HipChat API wrapper

Pythonic wrapper for the HipChat API. Closely follows the
official API naming and semantics, see https://www.hipchat.com/docs/api
for details.

Quickstart:

    import hipchat
    api = hipchat.api('YOUR_AUTH_TOKEN')
    rooms = api.rooms.list()  # list all rooms
    users = api.users.list()  # list all users

See also:

    api.data.Room
    api.data.User

"""

from .api import Api  # noqa
