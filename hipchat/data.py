import datetime


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
