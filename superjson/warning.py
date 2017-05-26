#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger("SuperJson")

WARN_MSG = ("IMPLEMENT WARNING! SuperJson.{attr} is not a valid "
            "{method_type} method! It must have 'self' as first argument, "
            "'{obj_or_dct}' as second argument, and 'class_name' as "
            "third argument with a default value. The default value is the "
            "object class name in dot notation, which is the string equals to "
            "what get_class_name(obj) returns. Example: "
            "def {dump_or_load}_set(self, {obj_or_dct}, "
            "class_name='builtins.set'):")


def prt_console(message, verbose):
    """Print message to console, if ``verbose`` is True. 
    """
    if verbose:
        logger.warning(message)
