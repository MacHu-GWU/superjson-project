#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.3"
__short_description__ = "Extendable json encode/decode library."
__license__ = "MIT"

try:
    from ._superjson import SuperJson, superjson as json, get_class_name
except Exception as e:
    pass
