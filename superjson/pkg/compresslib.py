#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
compress and decompress data using zlib.
"""

__version__ = "0.0.1"
__author__ = "Sanhe Hu"
__license__ = "MIT"

import sys
import types
import zlib
import base64
import pickle


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes

    MAXSIZE = sys.maxsize
else:
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str

__all__ = ["compress", "decompress"]


def _compress_obj(obj, level):
    """Compress object to bytes.
    """
    return zlib.compress(pickle.dumps(obj, protocol=2), level)


def _compress_str(s, level):
    """Compress str to bytes.
    """
    return zlib.compress(s.encode("utf-8"), level)


def _compress_bytes(b, level):
    """Compress bytes to bytes.
    """
    return zlib.compress(b, level)


def compress(obj, level=6, return_type="bytes"):
    """Compress anything to bytes or string.

    :params obj: 
    :params level: 
    :params return_type: if bytes, then return bytes; if str, then return
      base64.b64encode bytes in utf-8 string. 
    """
    if isinstance(obj, binary_type):
        b = zlib.compress(obj, level)
    elif isinstance(obj, string_types):
        b = zlib.compress(obj.encode("utf-8"), level)
    else:
        b = zlib.compress(pickle.dumps(obj, protocol=2), level)

    if return_type == "bytes":
        return b
    elif return_type == "str":
        return base64.b64encode(b).decode("utf-8")
    else:
        raise ValueError("'return_type' has to be one of 'bytes', 'str'!")


def decompress(obj, return_type="bytes"):
    """De-compress it to it's original.

    :params obj: Compressed object, could be bytes or str.
    :params return_type: if bytes, then return bytes; if str, then use 
      base64.b64decode; if obj, then use pickle.loads return an object. 
    """
    if isinstance(obj, binary_type):
        b = zlib.decompress(obj)
    elif isinstance(obj, string_types):
        b = zlib.decompress(base64.b64decode(obj.encode("utf-8")))
    else:
        raise TypeError("input cannot be anything other than str and bytes!")

    if return_type == "bytes":
        return b
    elif return_type == "str":
        return b.decode("utf-8")
    elif return_type == "obj":
        return pickle.loads(b)
    else:
        raise ValueError(
            "'return_type' has to be one of 'bytes', 'str' or 'obj'!")
