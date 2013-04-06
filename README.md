# A Pythonic wrapper for the HipChat API

The [HipChat API](https://www.hipchat.com/docs/api) is easy to use as-is,
but making requests manually still requires you to get your hands dirty.

Use this wrapper to avoid manual work and use a nice, simple and Pythonic
API to interface with HipChat. The wrapper closely follows the naming and
semantic of the official API so you can use the official documentation in
addition to the documentation provided here and in the package itself.

## Installation and requirements

Install from PyPi:

    pip install hipchat-api

The package requires [requests](http://docs.python-requests.org/en/latest/),
which will be installed automatically if you use `pip`.

## Quickstart

First, initialize the API wrapper with your `auth_token`:

    import hipchat
    api = hipchat.Api('your_auth_token')

Now, you can use the available methods:

    for room in api.rooms.list():
        print room.name, room.topic

    for user in api.users.list():
        print user.name, user.photo_url

    r = api.rooms.show(your_room_id)
    print r.topic
    r.topic = 'New Room Topic'

    r.message('Hello, Room!')

## TODO

This wrapper is work in progress, and there are still some things missing:

* User creation, modification and deletion wrappers
* Tests

Pull requests welcome! :-)

## License

Copyright (C) 2013. by Senko Rasic and the hipchat-api contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
