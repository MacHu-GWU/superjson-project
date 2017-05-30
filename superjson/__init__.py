#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.4"
__short_description__ = "Extendable json encode/decode library."
__license__ = "MIT"

try:
    from ._superjson import SuperJson, get_class_name, superjson as json
except Exception as e:
    pass
