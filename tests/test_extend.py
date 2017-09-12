#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
from superjson import SuperJson, get_class_name


class User(object):
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __repr__(self):
        return "User(id=%r, name=%r)" % (self.id, self.name)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name


User_class_name = get_class_name(User())


class MySuperJson(SuperJson):
    def dump_User(self, obj, class_name=User_class_name):
        key = "$" + class_name
        return {key: {"id": obj.id, "name": obj.name}}

    def load_User(self, dct, class_name=User_class_name):
        key = "$" + class_name
        return User(**dct[key])

    # pytest will change the module from __main__ to test_extend
    def dump_test_extend_User(self, obj, class_name="test_extend.User"):
        key = "$" + class_name
        return {key: {"id": obj.id, "name": obj.name}}

    def load_test_extend_User(self, dct, class_name="test_extend.User"):
        key = "$" + class_name
        return User(**dct[key])

    # other method
    def dump_someting(self):
        pass

    def load_something(self):
        pass

    dump_this = None
    load_this = None


json = MySuperJson()


class TestMySuperJson(object):
    def test_dumps_loads(self):
        data = {
            "int": 1,
            "str": "Hello",
            "user": User(id=1, name="Alice"),
        }
        s = json.dumps(data, pretty=True)
        data1 = json.loads(s)
        assert data == data1


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
