# -*- coding: utf-8 -*-

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
