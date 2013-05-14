from .data import HipchatObject

__all__ = ['User']


class User(HipchatObject):
    """HipChat User.

    The class wraps users API (methods that start with "users/") and
    the room information from the API responses.

    The main User attributes are `user_id` (the unique user ID) and
    `name` (human-readable username).

    The rest of the fields are explained here:
        https://www.hipchat.com/docs/api/method/users/show

    """
    attributes = ('user_id', 'name', 'mention_name', 'email', 'title',
        'photo_url', 'status', 'status_message')

    def __repr__(self):
        return '<User id=%s name="%s">' % (str(self.user_id), str(self))

    @classmethod
    def _parse(cls, data):
        obj = super(User, cls)._parse(data)
        obj.is_group_admin = bool(int(data.get('is_group_admin', 0)))
        obj.is_deleted = bool(int(data.get('is_deleted', 0)))
        obj.last_active = cls._parse_ts(data.get('last_active'))
        obj.created = cls._parse_ts(data.get('created'))
        return obj

    @classmethod
    def list(cls, include_deleted=False):
        """List users.

        Returns a list of `User` objects representing all the users this
        API has access to.

        If the optional `include_deleted` argument is True, the deleted
        users will also be listed (default is False, ie. the deleted
        users will not be listed).

        """
        data = cls.api._get('users/list',
            include_deleted='1' if include_deleted else '0')
        return [cls._parse(u) for u in data['users']]

    @classmethod
    def show(cls, user_id):
        """Get information about a user.

        Returns a `User` object with information about a single user,
        specified by the `user_id` argument.

        If there's no user with the specified ID, the
        `hipchat.api.NotFoundError` exception will be raised.

        """
        data = cls.api._get('users/show', user_id=str(user_id))
        return cls._parse(data['user'])
