#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from collections import OrderedDict, deque
from datetime import date, datetime
from superjson import json


def test():
    data = {
        "int": 1,
        "str": "Hello",
        "bytes": "Hello".encode("utf-8"),
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

    s = json.dumps(data, pretty=True)
    data1 = json.loads(s)
    assert data == data1


if __name__ == "__main__":
    import os
    pytest.main([os.path.basename(__file__), "--tb=native", "-s"])
