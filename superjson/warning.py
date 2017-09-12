#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger("SuperJson")
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

WARN_MSG = ("IMPLEMENT WARNING! SuperJson.{attr} is not a valid "
            "{method_type} method! It must have 'self' as first argument, "
            "'{obj_or_dct}' as second argument, and 'class_name' as "
            "third argument with a default value. The default value is the "
            "object class name in dot notation, which is the string equals to "
            "what get_class_name(obj) returns. Example: "
            "def {dump_or_load}_set(self, {obj_or_dct}, "
            "class_name='builtins.set'):")


def prt_console(message, verbose):  # pragma: no cover
    """Print message to console, if ``verbose`` is True.
    """
    if verbose:
        logger.info(message)


if __name__ == "__main__":
    prt_console("execute ...", True)
