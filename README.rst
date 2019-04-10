.. image:: https://readthedocs.org/projects/superjson/badge/?version=latest
    :target: https://superjson.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://travis-ci.org/MacHu-GWU/superjson-project.svg?branch=master
    :target: https://travis-ci.org/MacHu-GWU/superjson-project?branch=master

.. image:: https://codecov.io/gh/MacHu-GWU/superjson-project/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/MacHu-GWU/superjson-project

.. image:: https://img.shields.io/pypi/v/superjson.svg
    :target: https://pypi.python.org/pypi/superjson

.. image:: https://img.shields.io/pypi/l/superjson.svg
    :target: https://pypi.python.org/pypi/superjson

.. image:: https://img.shields.io/pypi/pyversions/superjson.svg
    :target: https://pypi.python.org/pypi/superjson

.. image:: https://img.shields.io/pypi/dm/superjson.svg
    :alt: PyPI - Downloads

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/superjson-project

------


.. image:: https://img.shields.io/badge/Link-Document-blue.svg
      :target: https://superjson.readthedocs.io/index.html

.. image:: https://img.shields.io/badge/Link-API-blue.svg
      :target: https://superjson.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
      :target: https://superjson.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
      :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
      :target: https://github.com/MacHu-GWU/superjson-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
      :target: https://github.com/MacHu-GWU/superjson-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
      :target: https://github.com/MacHu-GWU/superjson-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
      :target: https://pypi.org/pypi/superjson#files


Welcome to ``superjson`` Documentation
===============================================================================
Features:

1. **Support** for ``date``, ``datetime``, ``set``, ``OrderedDict``, ``deque``, ``pathlib.Path``, ``numpy.ndarray``, that the original `json <https://docs.python.org/3/library/json.html>`_ module can not serialize.
2. **Easy to extend to support any custom data type**, `SEE HOW <extend_>`_.
3. Allow ``// double slash started comments``, ``# Pound key started comments`` style **comment** in json file (Good for human/machine readable config file).
4. Use ``.gz`` for file extension, data will be **automatically compressed**.
5. **Atomic Write is ensured**, operation of overwriting an existing json file is atomic.


Built-in Support for many popular data type
-------------------------------------------------------------------------------
Original `json <https://docs.python.org/3/library/json.html>`_ module doesn't support ``date``, ``datetime``, ``set``, ``OrderedDict``, ``deque``, ``pathlib.Path``, ``numpy.ndarray``, but ``superjson`` does! **If you want me to add support for other data type**, please `submit here <https://github.com/MacHu-GWU/superjson-project/issues>`_.

.. code-block:: python

    >>> from pathlib import Path # or from pathlib_mate import PathCls as Path
    >>> from collections import OrderedDict, deque
    >>> from datetime import date, datetime
    >>> from superjson import json
    >>> import numpy as np

    >>> data = {
    ...     "int": 1,
    ...     "str": "Hello",
    ...     "bytes": "Hello".encode("utf-8"),
    ...     "date": date(2010, 1, 1),
    ...     "datetime": datetime(2020, 1, 1, 18, 30, 0, 500),
    ...     "set": set([
    ...         datetime(2000, 1, 1),
    ...         datetime(2000, 1, 2),
    ...     ]),
    ...     "deque": deque([
    ...         deque([1, 2]),
    ...         deque([3, 4]),
    ...     ]),
    ...     "ordereddict": OrderedDict([
    ...         ("b", OrderedDict([("b", 1), ("a", 2)])),
    ...         ("a", OrderedDict([("b", 1), ("a", 2)])),
    ...     ]),
    ...     "path": Path(__file__),
    ...     "array": np.array([
    ...         [1, 2],
    ...         [1.1, 2.2],
    ...         ["a", "b"],
    ...         [datetime.now(), datetime.now()],
    ...     ]),
    ... }

    >>> json.dumps(data, pretty=True)
    ...
    >>> json.dump(data, "data.gz", overwrite=True) # atomic write ensured
    ...


.. _extend:

Extend
-------------------------------------------------------------------------------

**Custom serializer for your Python Object is easy**.

1. suppose you have a ``class User: ...`` object defined in ``model.py``

.. code-block:: python

    >>> # it doesn't matter that how's the instance been constructed
    >>> class User(object):
    ...     def __init__(self, id, name):
    ...         self.id = id
    ...         self.name = name
    ...
    ...     def __repr__(self):
    ...         return "User(id=%r, name=%r)" % (self.id, self.name)

2. Make your ``MySuperJson`` **inherit from** ``superjson.SuperJson``.

.. code-block:: python

    # Add support to xxx.model.User
    >>> from superjson import SuperJson
    >>> class MySuperJson(SuperJson): pass

3. **Get the full class name** for ``User``.

.. code-block:: python

    >>> from superjson import get_class_name
    >>> user_class_name = get_class_name(User(id=1, name="Alice")) # a dummy user

    # or you can just do
    >>> user_class_name = "xxx.model.User"

4. Define encode method and decode method in this name convention ``dump_xxx``, ``load_xxx``. You just need to manually **transform the instance to a SuperJson serializable object**, a combination of dict, list, tuple, set, str, integer, float, datetime, bytes, etc. And **just construct the instance from the SuperJson serializable object we just defined**. In the ``User`` example, we dump a user to ``{"id": user.id, "name": user.name}``, and load a user from ``User(**dict_data)``.

.. code-block:: python

    # Add support to xxx.model.User
    >>> from xxx.model import User
    >>> from superjson import SuperJson, get_class_name

    >>> user_class_name = get_class_name(User(id=1, name="Alice")) # a dummy user

    >>> class MySuperJson(SuperJson):
    ...     # dumper method has three input argument, self, obj and class_name
    ...     def dump_User(self, obj, class_name=user_class_name):
    ...         return {"$" + class_name: {"id": obj.id, "name": obj.name}}
    ...
    ...     # loader method has three input argument, self, dct and class_name
    ...     def load_User(self, dct, class_name=user_class_name):
    ...         return User(**dct["$" + class_name])

5. The final code looks like:

.. code-block:: python

    # Add support to xxx.model.User
    >>> from xxx.model import User
    >>> from superjson import SuperJson, get_class_name

    >>> user_class_name = get_class_name(User(id=1, name="Alice")) # a dummy user

    >>> class MySuperJson(SuperJson):
    ...     # dumper method has three input argument, self, obj and class_name
    ...     def dump_User(self, obj, class_name=user_class_name):
    ...         return {"$" + class_name: {"id": obj.id, "name": obj.name}}
    ...
    ...     # loader method has three input argument, self, dct and class_name
    ...     def load_User(self, dct, class_name=user_class_name):
    ...         return User(**dct["$" + class_name])

    >>> json = MySuperJson()

    >>> a_complex_data = {"users": [User(id=1, name="Alice"), User(id=2, name="Bob")]}
    >>> s = json.dumps(p)
    >>> s
    {"users": [{"$xxx.model.User": {"id": 1, "name": "Alice"}}, {"$xxx.model.User": {"id": 2, "name": "Bob"}}]}
    >>> data = json.loads(s)
    >>> data
    {'users': [User(id=1, name='Alice'), User(id=2, name='Bob')]}


Comment
-------------------------------------------------------------------------------
You can add comments to your json file, and ``superjson`` **can still read it**!

.. code-block:: python

    >>> s= \
    """
    {
        # This is host
        "host": "127.0.0.1",
        "port": 8080 // This is port
    }
    """
    >>> config = json.loads(s, ignore_comments=True)
    >>> config
    {"host": "127.0.0.1", "port": 8080}


Compression
-------------------------------------------------------------------------------
Compress your json file is easy.

.. code-block:: python

    >>> import sys
    >>> data = {str(i): i for i in range(1000)}

    # Compress when dump to string
    >>> text = json.dumps(data, compress=True)

    # Decompress when load from compressed string
    >>> data1 = json.loads(text, decompress=True)

    # Auto compress when dump to file
    >>> json.dump(data, "data.gz") # "data.json" will not been compressed

    # Auto decompress when load from file
    >>> json.load("data.gz")

    # compare
    >>> text1 = json.dumps(data)
    >>> text2 = json.dumps(data, compress=True)
    >>> sys.getsizeof(text1)
    11829

    >>> sys.getsizeof(text2)
    5809


Advance file I/O utility method
-------------------------------------------------------------------------------
If your program is interrupted while writing, you got an incomplete file, and **you also lose the original file**! To solve this issue, ``json.dump(data, abspath, overwrite=True)`` method first write json to a temporary file, then rename to what you expect, and silently overwrite old one. This can **guarantee atomic write operation**.

.. code-block:: python

    >>> data = dict(a=1, b=2, c=3)
    # it first write to "data.gz.tmp", when it's done, overwrite the
    # original "data.gz" file
    >>> json.dump(data, abspath="data.gz", overwrite=True)

More options for ``dump``, ``load`` can be found :meth:`HERE <superjson._superjson.SuperJson.dump>`.


.. _install:

Install
------------------------------------------------------------------------------

``superjson`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install superjson

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade superjson
