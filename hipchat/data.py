import datetime
from iso8601 import parse_date

__all__ = ['Room', 'User', 'Message']


class HipchatObject(object):
    """HipChat data object.

    Internal class, inteded to be subclassed by the other objects
    representing data from HipChat API (Room, User, Message).

    Do not use directly.

    """
    attributes = []

    @classmethod
    def _parse(cls, data):
        obj = cls()
        for attr in cls.attributes:
            setattr(obj, attr, data.get(attr))
        return obj

    @staticmethod
    def _parse_ts(data):
        return datetime.datetime.fromtimestamp(data) if data else None

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


class Room(HipchatObject):
    """HipChat Room.

    The class wraps rooms API (methods that start with "rooms/") and
    the room information from the API responses.

    The main Room attributes are `room_id` (the unique room ID) and
    `name` (human-readable room name). There's also a `topic` property
    which can either be read (returns current room topic) or set
    (sets a new topic).

    The rest of the fields are explained here:
        https://www.hipchat.com/docs/api/method/rooms/show

    """
    attributes = ('xmpp_jid', 'name', 'is_archived', 'room_id',
        'owner_user_id', 'is_private', 'guest_access_url')

    def __repr__(self):
        return '<Room id=%s name="%s">' % (str(self.room_id), str(self))

    @classmethod
    def _parse(cls, data):
        obj = super(Room, cls)._parse(data)
        obj._topic = data['topic']
        obj.last_active = cls._parse_ts(data.get('last_active'))
        obj.created = cls._parse_ts(data.get('created'))
        if 'participants' in data:
            obj.participants = [cls.api.users._parse(p)
                for p in data['participants']]
        else:
            obj.participants = []

        return obj

    @classmethod
    def list(cls):
        """List rooms.

        Returns a list of `Room` objects representing the rooms this API
        has access to.

        """
        data = cls.api._get('rooms/list')
        return [cls._parse(r) for r in data['rooms']]

    @classmethod
    def show(cls, room_id):
        """Get information about a single room.

        Returns a `Room` object with information about the room specified by
        the `room_id` argument. If there's no room with that ID, the
        `hipchat.api.NotFoundError` exception will be raised.

        """
        data = cls.api._get('rooms/show', room_id=str(room_id))
        return cls._parse(data['room'])

    @property
    def topic(self):
        """Get or set the room topic.

        Getting the room topic doesn't involve any API calls since the topic
        was already returned with all the other room information.

        Setting the topic will perform an API call to update the room topic.

        """
        return self._topic

    @topic.setter
    def topic(self, value):
        self.api._post('rooms/topic', room_id=self.room_id,
            topic=value)
        self._topic = value

    def message(self, message, format='text', notify=False,
            color='yellow', frm='API'):
        """Send a message to the room.

        Sends a message with content `message` (either in text or html
        format, as specified by the `format` optional argument), using
        the specified `color`.

        If `notify` is True, the room participants will get notifications
        (depending on their settings) about the message.

        """
        self.api._post('rooms/message', **{
            'room_id': self.room_id,
            'message': message,
            'message_format': format,
            'notify': notify,
            'color': color,
            'from': frm
        })

    def history(self, date='recent', tz='UTC'):
        """Get room history.

        Retrieves messages from a given date (if date is a `datetime.date`
        object) or last 75 messages (if date is string "recent"). The
        optional `tz` argument specifies which timezone to use to determine
        when the day starts and ends.

        Returns a list of `Message` objects representing the messages.

        """
        if isinstance(date, datetime.date):
            date = date.strftime('%Y-%m-%d')
            if date > date.today():
                raise ValueError('')
        data = self.api._get('rooms/history', room_id=self.room_id,
            date=date, timezone=tz)
        return [Message._parse(m, self.api.users) for m in data['messages']]

    @classmethod
    def create(cls, name, owner_user_id, topic='', private=True,
            guest_access=False):
        """Create a room.

        Creates a new room with the specified `name` and sets the owner
        based on the provided `owner_user_id` (integer).

        If `topic` is provided, the initial room topic will be set to it. The
        default topic is "" (empty string).

        If `private` is True (default), only invited users will be
        able to join. If `guest_access` is True, HipChat will enable guest
        access to the room (default is guest access is disabled).

        Returns a `Room` object representing the newly created room.

        """
        data = cls.api._post('rooms/create', name=name,
            owner_user_id=owner_user_id, topic=topic,
            private='private' if private else 'public',
            guest_access='1' if guest_access else '0')
        return cls._parse(data['room'])

    def delete(self):
        """Delete the room.

        Be careful with this method, as there is no way of restoring
        deleted rooms or their histories.

        """
        self.api._post('rooms/delete', room_id=self.room_id)


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


class Message(HipchatObject):
    """HipChat Message.

    Represents a message to a HipChat room.

    The only attributes are `message` (the message content), `date`
    (when the message was sent) and `from_user` (`User` object representing
    the author of the message).

    Note that the `User` object in `from_user` will only have `name` and
    `user_id` arguments set. To get all other information about the user,
    `api.users.show()` method should be called.

    """
    attributes = ('message',)

    @classmethod
    def _parse(cls, data, user_class=User):
        obj = super(Message, cls)._parse(data)
        obj.date = parse_date(data['date'])
        obj.from_user = user_class._parse(data['from'])
        return obj

    def __unicode__(self):
        return self.message

    def __repr__(self):
        return '<Message msg="%s">' % str(self)
