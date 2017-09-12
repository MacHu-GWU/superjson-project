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

.. image:: https://img.shields.io/badge/Star_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/superjson-project


Welcome to ``superjson`` Documentation
===============================================================================
Features:

1. Support for ``date``, ``datetime``, ``set``, ``OrderedDict``, ``deque``, ``numpy.ndarray``, that the original `json <https://docs.python.org/3/library/json.html>`_ module can not serialize. `See example <Other data types_>`_.
2. Easy to extend to support any custom data type. `See example <Extend_>`_.
3. Allow ``// double slash started comments``, ``# Pound key started comments`` style comment in json file (Good for human/machine readable config file). `See example <Comment_>`_.
4. Provide a ``compress`` option to reduce the data size. `See example <Compression_>`_.
5. Advance file I/O utility method can prevent **overwrite**, **interruption**, and provide **auto compression by file extension**. `See example <Advance file I/O utility method_>`_.


Quick Links
-----------

- .. image:: https://img.shields.io/badge/Link-Document-red.svg
      :target: http://www.wbh-doc.com.s3.amazonaws.com/superjson/index.html

- .. image:: https://img.shields.io/badge/Link-API_Reference_and_Source_Code-red.svg
      :target: API reference and source code <http://www.wbh-doc.com.s3.amazonaws.com/superjson/py-modindex.html

- .. image:: https://img.shields.io/badge/Link-Install-red.svg
      :target: `install`_

- .. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
      :target: https://github.com/MacHu-GWU/superjson-project

- .. image:: https://img.shields.io/badge/Link-Submit_Issue_and_Feature_Request-blue.svg
      :target: https://github.com/MacHu-GWU/superjson-project/issues

- .. image:: https://img.shields.io/badge/Link-Download-blue.svg
      :target: https://pypi.python.org/pypi/superjson#downloads


Built-in Support for many popular data type
-------------------------------------------------------------------------------
Original `json <https://docs.python.org/3/library/json.html>`_ module doesn't support ``date``, ``datetime``, ``set``, ``OrderedDict``, ``deque``, ``numpy.ndarray``, but ``superjson`` does! **If you want me to add support for other data type**, please `submit here <https://github.com/MacHu-GWU/superjson-project/issues>`_.

.. code-block:: python

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
    ...     "array": np.array([
    ...         [1, 2],
    ...         [1.1, 2.2],
    ...         ["a", "b"],
    ...         [datetime.now(), datetime.now()],
    ...     ]),
    ... }

    >>> json.dumps(data, pretty=True)


Extend
-------------------------------------------------------------------------------
You can extend your Encoder/Decoder in this way:

1. Make your ``MyJson`` inherit from ``superjson.SuperJson``.
2. Define encode method and decode method in this name convention ``dump_xxx``, ``load_xxx``.
3. dumper method has to dump object to a json serializable dictionary, and use "$<class_name>" as the key.
4. dumper and loader method must have a second argument ``class_name``, it must have a default value equals to the class name you want to support. there's a method ``get_class_name`` can help you to find out what is the correct class name.

Example:

.. code-block:: python

    # Add support to pathlib.Path
    >>> from pathlib import Path
    >>> from superjson import SuperJson, get_class_name

    >>> class MySuperJson(SuperJson):
    ...     # dumper method has three input argument, self, obj and class_name
    ...     def dump_Path(self, obj, class_name="pathlib.Path"):
    ...         return {"$" + class_name: str(obj.absolute())}
    ...
    ...     # loader method has three input argument, self, dct and class_name
    ...     def load_Path(self, dct, class_name="pathlib.Path"):
    ...         return Path(dct["$" + class_name])
    ...
    ...     def dump_PosixPath(self, obj, class_name="pathlib.PosixPath"):
    ...         return {"$" + class_name: str(obj.absolute())}
    ...
    ...     def load_PosixPath(self, dct, class_name="pathlib.PosixPath"):
    ...         return Path(dct["$" + class_name])
    ...
    ...     def dump_WindowsPath(self, obj, class_name="pathlib.WindowsPath"):
    ...         return {"$" + class_name: str(obj.absolute())}
    ...
    ...     def load_WindowsPath(self, dct, class_name="pathlib.WindowsPath"):
    ...         return Path(dct["$" + class_name])

    >>> json = MySuperJson()

    >>> p = Path(__file__)
    >>> class_name = get_class_name(p) # this method can help you find your pathlib.PosixPath
    >>> s = json.dumps(p)
    >>> s
    {"$pathlib.WindowsPath": "C:\\Users\\admin\\superjson-project\\README.rst"}
    >>> p1 = json.loads(s)
    >>> p1
    C:\\Users\\admin\\superjson-project\\README.rst


Comment
-------------------------------------------------------------------------------
You can add comments to your json file, and ``superjson`` can still read it!

.. code-block:: json

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
    >>> s = json.dumps(data, compress=True)

    # Decompress when load from compressed string
    >>> data1 = json.loads(s, decompress=True)

    # Auto compress when dump to file
    >>> json.dump(data, "data.gz") # "data.json" will not been compressed

    # Auto decompress when load from file
    >>> json.load("data.gz")

    # compare
    >>> s1 = json.dumps(data)
    >>> s2 = json.dumps(data, compress=True)
    >>> sys.getsizeof(s1)
    11829

    >>> sys.getsizeof(s2)
    5809


Advance file I/O utility method
-------------------------------------------------------------------------------
If your program is interrupted while writing, you got an incomplete file, and **you also lose the original file**! To solve this issue, ``json.safe_dump(data, abspath)`` method first write json to a temporary file, then rename to what you expect, and silently overwrite old one. This can **guarantee atomic write operation**.

.. code-block:: python

    >>> data = dict(a=1, b=2, c=3)
    # it first write to "data.gz.tmp", when it's done, overwrite the
    # original "data.gz" file
    >>> json.safe_dump(data, "data.gz")

More options for ``dump``, ``safe_dump``, ``load`` can be found `HERE <http://www.wbh-doc.com.s3.amazonaws.com/superjson/_superjson.html#superjson._superjson.SuperJson.dump>`_.


.. _install:

Install
-------------------------------------------------------------------------------

``superjson`` is released on PyPI, so all you need is:

.. code-block:: console

	$ pip install superjson

To upgrade to latest version:

.. code-block:: console

	$ pip install --upgrade superjson