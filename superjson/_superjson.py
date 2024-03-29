# -*- coding: utf-8 -*-

import os
import json
import time
import inspect

from collections import OrderedDict, deque
from datetime import datetime
from base64 import b64encode, b64decode

from .helper import get_class_name
from .comments import strip_comments
from .warning import logger, WARN_MSG, prt_console
from .pkg import compresslib
from .pkg.atomicwrites import atomic_write


def get_class_name_from_dumper_loader_method(func):
    """
    Get default value of ``class_name`` argument.

    Because the third argument of dumper, loader method must be the class name.
    """
    return inspect.getfullargspec(func).defaults[0]


def is_dumper_method(func):
    """
    Test if it is a dumper method.
    """
    if inspect.getfullargspec(func).args == ["self", "obj", "class_name"]:
        return True
    else:
        return False


def is_loader_method(func):
    """
    Test if it is a loader method.
    """
    if inspect.getfullargspec(func).args == ["self", "dct", "class_name"]:
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

                # link dumper / loader method with the full classname
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


bytes_class_name = get_class_name(bytes())
set_class_name = get_class_name(set())


def is_compressed_json_file(abspath):
    """Test a file is a valid json file.

    - ``*.json``: uncompressed, utf-8 encode json file
    - ``*.js``: uncompressed, utf-8 encode json file
    - ``*.gz``: compressed, utf-8 encode json file
    """
    abspath = abspath.lower()
    fname, ext = os.path.splitext(abspath)
    if ext in [".json", ".js"]:
        is_compressed = False
    elif ext == ".gz":
        is_compressed = True
    else:
        raise ValueError(
            "'%s' is not a valid json file. "
            "extension has to be '.json' or '.js' for uncompressed, '.gz' "
            "for compressed." % abspath)
    return is_compressed


class BaseSuperJson(metaclass=Meta):
    """
    A extensable json encoder/decoder. You can easily custom converter for
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
                return {k: self._json_convert(v) for k, v in obj.items()}

        # nested dict
        elif isinstance(obj, dict):
            return {k: self._json_convert(v) for k, v in obj.items()}

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
            for key, value in dct.items():
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

    def dumps(
        self,
        obj,
        indent: bool = None,
        sort_keys: bool = None,
        pretty: bool = False,
        float_precision: int = None,
        ensure_ascii: bool = True,
        compress: bool = False,
        **kwargs
    ):
        """Dump any object into json string.

        :param pretty: if ``True``, dump json into pretty indent and sorted key
            format.
        :type pretty: bool

        :param float_precision: default ``None``, limit floats to
            N-decimal points.
        :type float_precision: int

        :param compress: default ``False``. If True, then compress encoded string.
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

    def loads(
        self,
        s: str,
        object_hook: bool = None,
        decompress: bool = False,
        ignore_comments: bool = False,
        **kwargs,
    ):
        """load object from json encoded string.

        :param decompress: default ``False``. If True, then decompress string.
        :type decompress: bool

        :param ignore_comments: default ``False``. If True, then ignore comments.
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

    def dump(
        self,
        obj,
        abspath: str,
        indent: bool = None,
        sort_keys: bool = None,
        pretty: bool = False,
        float_precision: int = None,
        ensure_ascii: bool = True,
        overwrite: bool = False,
        verbose: bool = True,
        **kwargs
    ):
        """Dump any object into file.

        :param abspath: if ``*.json, *.js**`` then do regular dump. if ``*.gz``,
          then perform compression.
        :type abspath: str

        :param pretty: if True, dump json into pretty indent and sorted key
          format.
        :type pretty: bool

        :param float_precision: default ``None``, limit floats to
          N-decimal points.
        :type float_precision: int

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

        if not overwrite:
            if os.path.exists(abspath):  # pragma: no cover
                prt_console(
                    "    Stop! File exists and overwrite is not allowed",
                    verbose,
                )
                return

        st = time.process_time()

        s = self.dumps(
            obj,
            indent=indent,
            sort_keys=sort_keys,
            pretty=pretty,
            float_precision=float_precision,
            ensure_ascii=ensure_ascii,
            compress=False,  # use uncompressed string, and directly write to file
            **kwargs,
        )

        with atomic_write(abspath, mode="wb", overwrite=True) as f:
            if is_compressed:
                f.write(compresslib.compress(s, return_type="bytes"))
            else:
                f.write(s.encode("utf-8"))

        prt_console(
            "    Complete! Elapse %.6f sec." % (time.process_time() - st),
            verbose,
        )
        return s

    def load(
        self,
        abspath: str,
        object_hook=None,
        ignore_comments: bool = False,
        verbose: bool = True,
        **kwargs
    ):
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

        st = time.process_time()

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
            **kwargs,
        )

        prt_console("    Complete! Elapse %.6f sec." % (time.process_time() - st),
                    verbose)

        return obj

    # ----------------------------------------------------------------------
    # Support built in data type
    # ----------------------------------------------------------------------
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
        try:
            from dateutil.parser import parse
        except ImportError:  # pragma: no cover
            msg = ("You need to install `python-dateutil` to support load/dump for datetime type")
            logger.info(msg)
            raise
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
                (key, self._json_convert(value)) for key, value in obj.items()
            ]
        }

    def load_OrderedDict(self, dct, class_name="collections.OrderedDict"):
        """
        ``collections.OrderedDict`` loader.
        """
        return OrderedDict(dct["$" + class_name])


class SuperJson(BaseSuperJson): pass


superjson = SuperJson()
