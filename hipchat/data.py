import datetime
from iso8601 import parse_date


class HipchatObject(object):

    attributes = []

    @classmethod
    def _parse(cls, data):
        obj = cls()
        for attr in cls.attributes:
            setattr(obj, attr, data.get(attr))
        return obj

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


class Room(HipchatObject):

    attributes = ('xmpp_jid', 'name', 'is_archived', 'room_id',
        'owner_user_id', 'is_private', 'guest_access_url')

    def __repr__(self):
        return '<Room id="%s" name="%s">' % (str(self.room_id), str(self))

    @classmethod
    def _parse(cls, data):
        obj = super(Room, cls)._parse(data)
        obj._topic = data['topic']
        obj.last_active = datetime.datetime.fromtimestamp(data['last_active'])
        obj.created = datetime.datetime.fromtimestamp(data['created'])
        if 'participants' in data:
            obj.participants = [cls.api.users._parse(p)
                for p in data['participants']]
        else:
            obj.participants = []

        return obj

    @classmethod
    def list(cls):
        data = cls.api._get('rooms/list')
        return [cls._parse(r) for r in data['rooms']]

    @classmethod
    def show(cls, room_id):
        data = cls.api._get('rooms/show', room_id=str(room_id))
        return cls._parse(data['room'])

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, value):
        self.api._post('rooms/topic', room_id=self.room_id,
            topic=value)
        self._topic = value

    def message(self, message, format='text', notify=False,
            color='yellow', frm='API'):
        data = self.api._post('rooms/message', **{
            'room_id': self.room_id,
            'message': message,
            'message_format': format,
            'notify': notify,
            'color': color,
            'from': frm
        })
        return data

    def history(self, date='recent', tz='UTC'):
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
        data = cls.api._post('rooms/create', name=name,
            owner_user_id=owner_user_id, topic=topic,
            private='private' if private else 'public',
            guest_access='1' if guest_access else '0')
        return cls._parse(data['room'])

    def delete(self):
        self.api._post('rooms/delete', room_id=self.room_id)


class User(HipchatObject):
    attributes = ('user_id', 'name', 'mention_name', 'email', 'title',
        'photo_url', 'status', 'status_message')

    def __repr__(self):
        return '<User id="%s" name="%s">' % (str(self.user_id), str(self))

    @classmethod
    def _parse(cls, data):
        obj = super(User, cls)._parse(data)
        obj.is_group_admin = bool(int(data['is_group_admin']))
        obj.is_deleted = bool(int(data['is_deleted']))
        obj.last_active = datetime.datetime.fromtimestamp(data['last_active'])
        obj.created = datetime.datetime.fromtimestamp(data['created'])
        return obj

    @classmethod
    def list(cls, include_deleted=False):
        data = cls.api._get('users/list',
            include_deleted='1' if include_deleted else '0')
        return [cls._parse(u) for u in data['users']]

    @classmethod
    def show(cls, user_id):
        data = cls.api._get('users/show', user_id=str(user_id))
        return cls._parse(data['user'])


class Message(HipchatObject):
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
