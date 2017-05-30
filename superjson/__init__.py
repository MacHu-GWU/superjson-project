#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 
"""

__version__ = "0.0.1"
__short_description__ = "Super Json."
__license__ = "MIT"

try:
    from ._superjson import SuperJson, superjson as json, get_class_name
except Exception as e:
    pass
