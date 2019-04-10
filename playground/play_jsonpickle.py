# -*- coding: utf-8 -*-

"""
Why not jsonpickle?

`jsonpickle <http://jsonpickle.github.io/>`_ is an awesome library. It converts
any python object into json. Internally, jsonpickle use pickle to serialize python object as binary data, and base64 encode it.

But, pickled data in python2 and python3 are not compatible. In other word, **a json made by one machine may not be readable on another machine**.

In addition, jsonpickle doesn't allow users to create their own serializer very easily.

That's the reason why I create superjson.
"""

import jsonpickle
from collections import OrderedDict, deque
from datetime import datetime

data = {
    "a_datetime": datetime.now(),
    "a_set": {1, 2, 3},
    "a_ordereddict": OrderedDict([("a", 1), ("b", 2), ("c", 3)]),
    "a_deque": deque([3, 2, 1]),
}
s = jsonpickle.dumps(data)
print(s)
