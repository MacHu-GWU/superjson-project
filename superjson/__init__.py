# -*- coding: utf-8 -*-

from ._version import __version__

__short_description__ = "Extendable json encode/decode library."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__maintainer__ = "Sanhe Hu"
__maintainer_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

try:
    from ._superjson import SuperJson, get_class_name, superjson as json
except ImportError as e:  # pragma: no cover
    pass
except Exception as e:  # pragma: no cover
    raise e
