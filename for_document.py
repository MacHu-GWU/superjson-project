#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from superjson import SuperJson, get_class_name

class MySuperJson(SuperJson):
    def dump_Path(self, obj, class_name="pathlib.Path"):
        return {"$" + class_name: str(obj.absolute())}

    def load_Path(self, dct, class_name="pathlib.Path"):
        return Path(dct["$" + class_name])
    
    def dump_PosixPath(self, obj, class_name="pathlib.PosixPath"):
        return {"$" + class_name: str(obj.absolute())}

    def load_PosixPath(self, dct, class_name="pathlib.PosixPath"):
        return Path(dct["$" + class_name])
    
    def dump_WindowsPath(self, obj, class_name="pathlib.WindowsPath"):
        return {"$" + class_name: str(obj.absolute())}

    def load_WindowsPath(self, dct, class_name="pathlib.WindowsPath"):
        return Path(dct["$" + class_name])

json = MySuperJson()


if __name__ == "__main__":
    p = Path(__file__)
    class_name = get_class_name(p)
    s = json.dumps(p)
    print(s)
    p1 = json.loads(s)
    assert p == p1

    import random
    
    data = {str(i): i for i in range(1000)}
    s1 = json.dumps(data)
    s2 = json.dumps(data, compress=True)
    print(sys.getsizeof(s1))
    print(sys.getsizeof(s2))