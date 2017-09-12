#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import shutil
import inspect

from collections import OrderedDict, deque
from datetime import datetime
from base64 import b64encode, b64decode

try:
    import numpy as np
except ImportError:  # pragma: no cover
    pass

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pass

try:
    from .comments import strip_comments
    from .warning import logger, WARN_MSG, prt_console
    from .pkg import compresslib
    from .pkg.six import PY2, PY3, add_metaclass, string_types, iteritems
    from .pkg.dateutil.parser import parse
except:  # pragma: no cover
    from superjson.comments import strip_comments
    from superjson.warning import logger, WARN_MSG, prt_console
    from superjson.pkg import compresslib
    from superjson.pkg.six import PY2, PY3, add_metaclass, string_types, iteritems
    from superjson.pkg.dateutil.parser import parse


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


if PY2:  # pragma: no cover
    bytes_class_name = "__builtin__.str"
    set_class_name = "__builtin__.set"
elif PY3:  # pragma: no cover
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

        # float
        elif isinstance(obj, float):
            return float(json.encoder.FLOAT_REPR(obj))

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

    def _object_hook2(self, dct):  # pragma: no cover
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
            raise EnvironmentError("'%s' doesn't exist." % abspath)

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
        """
        ``btyes`` dumper.
        """
        return {"$" + class_name: b64encode(obj).decode()}

    def load_bytes(self, dct, class_name=bytes_class_name):
        """
        ``btyes`` loader.
        """
        return b64decode(dct["$" + class_name].encode())

    def dump_datetime(self, obj, class_name="datetime.datetime"):
        """
        ``datetime.datetime`` dumper.
        """
        return {"$" + class_name: obj.isoformat()}

    def load_datetime(self, dct, class_name="datetime.datetime"):
        """
        ``datetime.datetime`` loader.
        """
        return parse(dct["$" + class_name])

    def dump_date(self, obj, class_name="datetime.date"):
        """
        ``datetime.date`` dumper.
        """
        return {"$" + class_name: str(obj)}

    def load_date(self, dct, class_name="datetime.date"):
        """
        ``datetime.date`` loader.
        """
        return datetime.strptime(dct["$" + class_name], "%Y-%m-%d").date()

    def dump_set(self, obj, class_name=set_class_name):
        """
        ``set`` dumper.
        """
        return {"$" + class_name: [self._json_convert(item) for item in obj]}

    def load_set(self, dct, class_name=set_class_name):
        """
        ``set`` loader.
        """
        return set(dct["$" + class_name])

    def dump_deque(self, obj, class_name="collections.deque"):
        """
        ``collections.deque`` dumper.
        """
        return {"$" + class_name: [self._json_convert(item) for item in obj]}

    def load_deque(self, dct, class_name="collections.deque"):
        """
        ``collections.deque`` loader.
        """
        return deque(dct["$" + class_name])

    def dump_OrderedDict(self, obj, class_name="collections.OrderedDict"):
        """
        ``collections.OrderedDict`` dumper.
        """
        return {
            "$" + class_name: [
                (key, self._json_convert(value)) for key, value in iteritems(obj)
            ]
        }

    def load_OrderedDict(self, dct, class_name="collections.OrderedDict"):
        """
        ``collections.OrderedDict`` loader.
        """
        return OrderedDict(dct["$" + class_name])

    def dump_nparray(self, obj, class_name="numpy.ndarray"):
        """
        ``numpy.ndarray`` dumper.
        """
        return {"$" + class_name: self._json_convert(obj.tolist())}

    def load_nparray(self, dct, class_name="numpy.ndarray"):
        """
        ``numpy.ndarray`` loader.
        """
        return np.array(dct["$" + class_name])


superjson = SuperJson()
