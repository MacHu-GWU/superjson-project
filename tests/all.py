# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import date, datetime
from collections import OrderedDict, deque

data = {
    "int": 1,
    "float": 3.1415926535897932626,
    "str": "Hello",
    "bytes": "Hello".encode("utf-8"),
    "list": [1.111111, 2.222222, 3.3333333],
    "dict": {"yes": True, "no": False, "null": None},
    "date": date(2010, 1, 1),
    "datetime": datetime(2020, 1, 1, 18, 30, 0, 500),
    "set": set([
        datetime(2000, 1, 1),
        datetime(2000, 1, 2),
    ]),
    "deque": deque([
        deque([1, 2]),
        deque([3, 4]),
    ]),
    "ordereddict": OrderedDict([
        ("b", OrderedDict([("b", 1), ("a", 2)])),
        ("a", OrderedDict([("b", 1), ("a", 2)])),
    ]),
}


if __name__ == "__main__":
    import pytest

    pytest.main(["-s", "--tb=native"])
