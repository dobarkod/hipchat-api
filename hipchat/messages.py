from iso8601 import parse_date

from .data import HipchatObject
from .users import User

__all__ = ['Message']


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
