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
        'photo_url', 'status', 'status_message', 'password')

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

    @staticmethod
    def _maybe_dict(**kwargs):
        return dict((k,v) for k,v in kwargs.iteritems() if v is not None)

    @classmethod
    def create(cls, email, name, mention_name=None, title=None,
            is_group_admin=False, password=None, timezone='UTC'):
        """Create a new user.

        Creates a new user with the provided `email` and full `name`.

        If `password` is not provided, the response will contain the newly
        created user's randomly generated password.

        The user's `mention_name` specifies what will trigger mention
        notification. If not set, it defaults to the full name. The optional
        `title` (is set) specifies the user's title.

        If `is_group_admin` is True, the newly created user will be added
        to group admins.

        The optional `timezone` argument (string) sets the user's timezone.
        If not set, defaults to 'UTC'.

        Returns a `User` object representing the newly created user. If the
        password wasn't provided in the request, the initial password for
        the user is returned in the `password` attribute. It should be recorded
        (or changed) immediately as this is the only time it will be returned.

        """
        params = cls._maybe_dict(email=email, name=name, timezone=timezone,
            is_group_admin='1' if is_group_admin else '0',
            mention_name=mention_name, title=title, password=password)
        data = cls.api._post('users/create', **params)
        return cls._parse(data['user'])

    def delete(self):
        """Delete the user.

        Deleted users are immediately disconnected from the chat.

        """
        self.api._post('users/delete', user_id=self.user_id)

    @classmethod
    def undelete(self, user_id=None, user_email=None):
        """Undelete a user.

        Undelete the user specified by either `user_id` (user's ID in the
        system) or `user_email` (their e-mail).

        The user will be sent a confirmation link via email.

        """
        if user_id is not None and user_email is not None:
            raise ValueError('only one of user_id or user_email should '
                'be provided, not both')

        if user_id is None and user_email is None:
            raise ValueError('either user_id or user_email should be provided')

        self.api._post('users/undelete',
            user_id=user_id if user_id is not None else user_email)

    def update(self, email=None, name=None, mention_name=None, title=None,
            is_group_admin=None, password=None, timezone=None):
        """Update user information.

        """
        params = self._maybe_dict(email=email, name=name, mention_name=None,
            is_group_admin=str(int(bool(is_group_admin)))
            if is_group_admin is not None else None,
            password=password, timezone=timezone)
        self.api._post('users/update', user_id=self.user_id, **params)
