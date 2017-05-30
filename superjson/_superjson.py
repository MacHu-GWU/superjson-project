#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import json
import time
import zlib
import base64
import shutil
import inspect
from six import PY2, PY3, add_metaclass, string_types, iteritems

from collections import OrderedDict, deque
from datetime import date, datetime
from base64 import b64encode, b64decode
from dateutil.parser import parse

try:
    from . import compresslib
    from .comments import strip_comments
    from .warning import logger, WARN_MSG, prt_console
    from .util import write, read
except:
    from superjson import compresslib
    from superjson.comments import strip_comments
    from superjson.warning import logger, WARN_MSG, prt_console
    from superjson.util import write, read

try:
    import numpy as np
except:
    pass

try:
    import pandas as pd
except:
    pass


def get_class_name(obj):
    """Get class name in dot separete notation

        >>> from datetime import datetime
        >>> obj = datetime.datetime(2000, 1, 1)
        >>> get_class_name(obj) -> "datetime.datetime"

        >>> from collections import deque
        >>> obj = deque([1, 2, 3])
        >>> get_class_name(obj) -> "collections.deque"
    """
    return obj.__class__.__module__ + "." + obj.__class__.__name__


def get_class_name_from_dumper_loader_method(func):
    """Get default value of ``class_name`` argument.

    Because the third argument of dumper, loader method must be the class name.

    """
    return inspect.getargspec(func).defaults[0]


def is_dumper_method(func):
    """Test if it is a dumper method.
    """
    if inspect.getargspec(func).args == ["self", "obj", "class_name"]:
        return True
    else:
        return False


def is_loader_method(func):
    """Test if it is a loader method.
    """
    if inspect.getargspec(func).args == ["self", "dct", "class_name"]:
        return True
    else:
        return False


class Meta(type):

    def __new__(cls, name, bases, attrs):
        klass = super(Meta, cls).__new__(cls, name, bases, attrs)

        _dumpers = dict()
        _loaders = dict()

        for base in inspect.getmro(klass):
            for attr, value in base.__dict__.items():
                dumper_warning_message = WARN_MSG.format(
                    attr=attr,
                    method_type="dumper",
                    obj_or_dct="obj",
                    dump_or_load="dump",
                )

                loader_warning_message = WARN_MSG.format(
                    attr=attr,
                    method_type="loader",
                    obj_or_dct="dct",
                    dump_or_load="load",
                )

                # find dumper method,
                if attr.startswith("dump_"):
                    try:
                        if is_dumper_method(value):
                            class_name = get_class_name_from_dumper_loader_method(
                                value)
                            _dumpers[class_name] = value
                        else:
                            logger.warning(dumper_warning_message)
                    except TypeError:
                        logger.warning(dumper_warning_message)

                # find loader method
                if attr.startswith("load_"):
                    try:
                        if is_loader_method(value):
                            class_name = get_class_name_from_dumper_loader_method(
                                value)
                            _loaders[class_name] = value
                        else:
                            logger.warning(loader_warning_message)
                    except TypeError:
                        logger.warning(loader_warning_message)

        klass._dumpers = _dumpers
        klass._loaders = _loaders
        return klass


if PY2:
    bytes_class_name = "builtins.str"
    set_class_name = "__builtin__.set"
elif PY3:
    bytes_class_name = "builtins.bytes"
    set_class_name = "builtins.set"


def is_compressed_json_file(abspath):
    """Test a file is a valid json file.

    - *.json: uncompressed, utf-8 encode json file
    - *.js: uncompressed, utf-8 encode json file
    - *.gz: compressed, utf-8 encode json file
    """
    abspath = abspath.lower()
    fname, ext = os.path.splitext(abspath)
    if ext in [".json", ".js"]:
        is_compressed = False
    elif ext == ".gz":
        is_compressed = True
    elif ext == ".tmp":
        return is_compressed_json_file(fname)
    else:
        raise ValueError(
            "'%s' is not a valid json file. "
            "extension has to be '.json' or '.js' for uncompressed, '.gz' "
            "for compressed." % abspath)
    return is_compressed


@add_metaclass(Meta)
class SuperJson(object):
    """A extensable json encoder/decoder. You can easily custom converter for 
    any types.
    """
    _dumpers = dict()
    _loaders = dict()

    def _dump(self, obj):
        """Dump single object to json serializable value.
        """
        class_name = get_class_name(obj)
        if class_name in self._dumpers:
            return self._dumpers[class_name](self, obj)
        raise TypeError("%r is not JSON serializable" % obj)

    def _json_convert(self, obj):
        """Recursive helper method that converts dict types to standard library
        json serializable types, so they can be converted into json.
        """
        # OrderedDict
        if isinstance(obj, OrderedDict):
            try:
                return self._dump(obj)
            except TypeError:
                return {k: self._json_convert(v) for k, v in iteritems(obj)}

        # nested dict
        elif isinstance(obj, dict):
            return {k: self._json_convert(v) for k, v in iteritems(obj)}

        # list or tuple
        elif isinstance(obj, (list, tuple)):
            return list((self._json_convert(v) for v in obj))

        # single object
        try:
            return self._dump(obj)
        except TypeError:
            return obj

    def _object_hook1(self, dct):
        """A function can convert dict data into object. 

        it's an O(1) implementation. 
        """
        # {"$class_name": obj_data}
        if len(dct) == 1:
            for key, value in iteritems(dct):
                class_name = key[1:]
                if class_name in self._loaders:
                    return self._loaders[class_name](self, dct)
            return dct
        return dct

    def _object_hook2(self, dct):
        """Another object hook implementation.

        it's an O(N) implementation.
        """
        for class_name, loader in self._loaders.items():
            if ("$" + class_name) in dct:
                return loader(self, dct)
        return dct

    def dumps(self, obj,
              indent=None,
              sort_keys=None,
              pretty=False,
              float_precision=None,
              ensure_ascii=True,
              compress=False,
              **kwargs):
        """Dump any object into json string.

        :param pretty: if True, dump json into pretty indent and sorted key
          format.
        :type pretty: bool

        :param float_precision: default ``None``, limit floats to 
          N-decimal points. 
        :type float_precision: integer

        :param compress: default ``False. If True, then compress encoded string.
        :type compress: bool
        """
        if pretty:
            indent = 4
            sort_keys = True

        if float_precision is None:
            json.encoder.FLOAT_REPR = repr
        else:
            json.encoder.FLOAT_REPR = lambda x: format(
                x, ".%sf" % float_precision)

        s = json.dumps(
            self._json_convert(obj),
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii,
            **kwargs
        )

        if compress:
            s = compresslib.compress(s, return_type="str")

        return s

    def loads(self, s,
              object_hook=None,
              decompress=False,
              ignore_comments=False,
              **kwargs):
        """load object from json encoded string.

        :param decompress: default ``False. If True, then decompress string.
        :type decompress: bool

        :param ignore_comments: default ``False. If True, then ignore comments.
        :type ignore_comments: bool
        """
        if decompress:
            s = compresslib.decompress(s, return_type="str")

        if ignore_comments:
            s = strip_comments(s)

        if object_hook is None:
            object_hook = self._object_hook1

        if "object_pairs_hook" in kwargs:
            del kwargs["object_pairs_hook"]

        obj = json.loads(
            s,
            object_hook=object_hook,
            object_pairs_hook=None,
            **kwargs
        )

        return obj

    def dump(self, obj,
             abspath,
             indent=None,
             sort_keys=None,
             pretty=False,
             float_precision=None,
             ensure_ascii=True,
             overwrite=False,
             verbose=True,
             **kwargs):
        """Dump any object into file.

        :param abspath: if ``*.json, *.js** then do regular dump. if ``*.gz``,
          then perform compression.
        :type abspath: str

        :param pretty: if True, dump json into pretty indent and sorted key
          format.
        :type pretty: bool

        :param float_precision: default ``None``, limit floats to 
          N-decimal points. 
        :type float_precision: integer

        :param overwrite: default ``False``, If ``True``, when you dump to 
          existing file, it silently overwrite it. If ``False``, an alert 
          message is shown. Default setting ``False`` is to prevent overwrite 
          file by mistake.
        :type overwrite: boolean

        :param verbose: default True, help-message-display trigger.
        :type verbose: boolean
        """
        prt_console("\nDump to '%s' ..." % abspath, verbose)

        is_compressed = is_compressed_json_file(abspath)

        if os.path.exists(abspath):
            if not overwrite:
                prt_console(
                    "    Stop! File exists and overwrite is not allowed",
                    verbose,
                )
                return

        st = time.clock()

        s = self.dumps(
            obj,
            indent=indent,
            sort_keys=sort_keys,
            pretty=pretty,
            float_precision=float_precision,
            ensure_ascii=ensure_ascii,
            # use uncompressed string, and directly write to file
            compress=False,
            **kwargs
        )

        with open(abspath, "wb") as f:
            if is_compressed:
                f.write(compresslib.compress(s, return_type="bytes"))
            else:
                f.write(s.encode("utf-8"))

        prt_console("    Complete! Elapse %.6f sec." % (time.clock() - st),
                    verbose)
        return s

    def safe_dump(self, obj,
                  abspath,
                  indent=None,
                  sort_keys=None,
                  pretty=False,
                  float_precision=None,
                  ensure_ascii=True,
                  verbose=True,
                  **kwargs):
        """A stable version of :func:`SuperJson.dump`, this method will 
        silently overwrite existing file.

        There's a issue with :func:`SuperJson.dump`: If your program is 
        interrupted while writing, you got an incomplete file, and you also 
        lose the original file. So this method write json to a temporary file 
        first, then rename to what you expect, and silently overwrite old one. 
        This way can guarantee atomic write operation.

        **中文文档**

        在对文件进行写入时, 如果程序中断, 则会留下一个不完整的文件。如果使用了
        覆盖式写入, 则我们即没有得到新文件, 同时也丢失了原文件。所以为了保证
        写操作的原子性(要么全部完成, 要么全部都不完成), 更好的方法是: 首先将
        文件写入一个临时文件中, 完成后再讲文件重命名, 覆盖旧文件。这样即使中途
        程序被中断, 也仅仅是留下了一个未完成的临时文件而已, 不会影响原文件。
        """
        abspath_temp = "%s.tmp" % abspath
        s = self.dump(
            obj,
            abspath_temp,
            indent=indent,
            sort_keys=sort_keys,
            pretty=pretty,
            float_precision=float_precision,
            ensure_ascii=ensure_ascii,
            overwrite=True,
            verbose=verbose,
            **kwargs
        )
        shutil.move(abspath_temp, abspath)
        return s

    def load(self, abspath,
             object_hook=None,
             ignore_comments=False,
             verbose=True,
             **kwargs):
        """load object from json file.

        :param abspath: if ``*.json, *.js** then do regular dump. if ``*.gz``,
          then perform decompression.
        :type abspath: str

        :param ignore_comments: default ``False. If True, then ignore comments.
        :type ignore_comments: bool

        :param verbose: default True, help-message-display trigger.
        :type verbose: boolean
        """
        prt_console("\nLoad from '%s' ..." % abspath, verbose)

        is_compressed = is_compressed_json_file(abspath)

        if not os.path.exists(abspath):
            raise ValueError("'%s' doesn't exist." % abspath)
            raise

        st = time.clock()

        with open(abspath, "rb") as f:
            if is_compressed:
                s = compresslib.decompress(f.read(), return_type="str")
            else:
                s = f.read().decode("utf-8")

        obj = self.loads(
            s,
            object_hook=object_hook,
            decompress=False,
            ignore_comments=ignore_comments,
        )

        prt_console("    Complete! Elapse %.6f sec." % (time.clock() - st),
                    verbose)

        return obj

    def dump_bytes(self, obj, class_name=bytes_class_name):
        return {"$" + class_name: b64encode(obj).decode()}

    def load_bytes(self, dct, class_name=bytes_class_name):
        return b64decode(dct["$" + class_name].encode())

    def dump_datetime(self, obj, class_name="datetime.datetime"):
        return {"$" + class_name: obj.isoformat()}

    def load_datetime(self, dct, class_name="datetime.datetime"):
        return parse(dct["$" + class_name])

    def dump_date(self, obj, class_name="datetime.date"):
        return {"$" + class_name: str(obj)}

    def load_date(self, dct, class_name="datetime.date"):
        return datetime.strptime(dct["$" + class_name], "%Y-%m-%d").date()

    def dump_set(self, obj, class_name=set_class_name):
        return {"$" + class_name: [self._json_convert(item) for item in obj]}

    def load_set(self, dct, class_name=set_class_name):
        return set(dct["$" + class_name])

    def dump_deque(self, obj, class_name="collections.deque"):
        return {"$" + class_name: [self._json_convert(item) for item in obj]}

    def load_deque(self, dct, class_name="collections.deque"):
        return deque(dct["$" + class_name])

    def dump_OrderedDict(self, obj, class_name="collections.OrderedDict"):
        return {
            "$" + class_name: [
                (key, self._json_convert(value)) for key, value in iteritems(obj)
            ]
        }

    def load_OrderedDict(self, dct, class_name="collections.OrderedDict"):
        return OrderedDict(dct["$" + class_name])

    def dump_nparray(self, obj, class_name="numpy.ndarray"):
        return {"$" + class_name: self._json_convert(obj.tolist())}

    def load_nparray(self, dct, class_name="numpy.ndarray"):
        return np.array(dct["$" + class_name])


superjson = SuperJson()


if __name__ == "__main__":
    from pprint import pprint

    def test_common():
        data = {
            "int": 1,
            "str": "Hello",
            "bytes": "Hello".encode("utf-8"),
            "date": date.today(),
            "datetime": datetime.now(),
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
        s = superjson.dumps(data, indent=4)
#         print(s)
        data1 = superjson.loads(s)
#         pprint(data1)
        assert data == data1

        s = superjson.dumps(data, compress=True)
#         print(s)
        data1 = superjson.loads(s, decompress=True)
#         pprint(data1)
        assert data == data1

    test_common()

    def test_numpy():
        data = {
            "ndarray_int": np.array([[1, 2], [3, 4]]),
            "ndarray_float": np.array([[1.1, 2.2], [3.3, 4.4]]),
            "ndarray_str": np.array([["a", "b"], ["c", "d"]]),
            "ndarray_datetime": np.array(
                [datetime(2000, 1, 1), datetime(2010, 1, 1)]
            ),
        }
        s = superjson.dumps(data, indent=4)
#         print(s)
        data1 = superjson.loads(s)
#         pprint(data1)

        for key in data:
            assert np.array_equal(data[key], data1[key])

    test_numpy()

    def test_pandas():
        """

        .. note:: Not supported yet!
        """
        data = {
            "series": pd.Series([("a", datetime(2000, 1, 1)),
                                 ("b", datetime(2010, 1, 1))]),
        }
#         s = superjson.dumps(data, indent=4)
#         print(s)
#         data1 = superjson.loads(s)
#         pprint(data1)

#     test_pandas()

    def test_extend():
        """Test for extend SuperJson for arbitrary custom types.
        """
        from sfm.nameddict import Base as Address

        class User(object):

            def __init__(self, id=None, name=None):
                self.id = id
                self.name = name

            def __repr__(self):
                return "User(id=%r, name=%r)" % (self.id, self.name)

            def __eq__(self, other):
                return self.id == other.id and self.name == other.name

        Address_class_name = "sfm.nameddict.Base"
        assert get_class_name(Address()) == "sfm.nameddict.Base"

        User_class_name = "__main__.User"
        assert get_class_name(User()) == "__main__.User"

        class MySuperJson(SuperJson):

            def dump_User(self, obj, class_name="__main__.User"):
                key = "$" + class_name
                return {key: {"id": obj.id, "name": obj.name}}

            def load_User(self, dct, class_name="__main__.User"):
                key = "$" + class_name
                return User(**dct[key])

            def dump_Address(self, obj, class_name="sfm.nameddict.Base"):
                key = "$" + class_name
                return {key: {"street": obj.street,
                              "city": obj.city,
                              "state": obj.state,
                              "zipcode": obj.zipcode}}

            def load_Address(self, dct, class_name="sfm.nameddict.Base"):
                key = "$" + class_name
                return Address(**dct[key])

        js = MySuperJson()
        data = {
            "int": 1,
            "str": "Hello",
            "user": User(id=1, name="Alice"),
            "address": Address(
                street="123 Main St", city="New York", state="NY", zipcode="10001",
            ),
        }
        s = js.dumps(data, indent=4)
#         print(s)

        data1 = js.loads(s)
#         print(data1)

        assert data == data1

    test_extend()
