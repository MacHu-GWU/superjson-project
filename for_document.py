# -*- coding: utf-8 -*-

import sys
from superjson import SuperJson, get_class_name


class User(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return "User(id=%r, name=%r)" % (self.id, self.name)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name


user_class_name = get_class_name(User(id=1, name="Alice"))


class MySuperJson(SuperJson):
    def dump_User(self, obj, class_name=user_class_name):
        return {"$" + class_name: {"id": obj.id, "name": obj.name}}

    def load_User(self, dct, class_name=user_class_name):
        return User(**dct["$" + class_name])


json = MySuperJson()

if __name__ == "__main__":
    a_complex_data = {"users": [User(id=1, name="Alice"), User(id=2, name="Bob")]}
    s = json.dumps(a_complex_data)
    print(s)
    a_complex_data1 = json.loads(s)
    print(a_complex_data1)
    assert a_complex_data == a_complex_data1

    data = {str(i): i for i in range(1000)}
    s1 = json.dumps(data)
    s2 = json.dumps(data, compress=True)
    print(sys.getsizeof(s1))
    print(sys.getsizeof(s2))
