import datetime

from .data import HipchatObject
from .messages import Message

__all__ = ['Room']


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

    def history(self, date='recent', timezone='UTC'):
        """Get room history.

        Retrieves messages from a given date (if date is a `datetime.date`
        object) or last 75 messages (if date is string "recent"). The
        optional `timezone` argument specifies which timezone to use to
        determine when the day starts and ends.

        Returns a list of `Message` objects representing the messages.

        """
        if isinstance(date, datetime.date):
            date = date.strftime('%Y-%m-%d')
            if date > date.today():
                raise ValueError('')
        data = self.api._get('rooms/history', room_id=self.room_id,
            date=date, timezone=timezone)
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
