.. image:: https://travis-ci.org/MacHu-GWU/superjson-project.svg?branch=master

.. image:: https://img.shields.io/pypi/v/superjson.svg

.. image:: https://img.shields.io/pypi/l/superjson.svg

.. image:: https://img.shields.io/pypi/pyversions/superjson.svg


Welcome to superjson Documentation
===============================================================================
Features:

1. support for ``date``, ``datetime``, ``set``, ``OrderedDict``, ``deque``, ``numpy.ndarray`` that original json module not serializable.
2. easy to extend to support any custom type.
3. allow ``// comment``, ``# comment`` style comment in json file (Good for config file).
4. provide a ``compress`` option.
5. advance file I/O utility method can prevent **overwrite**, **interruption**, **auto compression by file extension**.


**Quick Links**
-------------------------------------------------------------------------------
- `GitHub Homepage <https://github.com/MacHu-GWU/superjson-project>`_
- `Online Documentation <http://pythonhosted.org/superjson>`_
- `PyPI download <https://pypi.python.org/pypi/superjson>`_
- `Install <install_>`_
- `Issue submit and feature request <https://github.com/MacHu-GWU/superjson-project/issues>`_
- `API reference and source code <http://pythonhosted.org/superjson/py-modindex.html>`_


Other data types
-------------------------------------------------------------------------------
.. code-block:: python

    >>> from collections import OrderedDict, deque
    >>> from datetime import date, datetime
    >>> from superjson import json

    >>> data = {
            "int": 1,
            "str": "Hello",
            "bytes": "Hello".encode("utf-8"),
            "date": date(2010, 1, 1),
            "datetime": datetime(2020, 1, 1, 18, 30, 0, 500),
            "set": set([
                datetime(2000, 1, 1),
                datetime(2000, 1, 2),
            ]),
            "deque": deque([
                deque([1, 2]),
                deque([3, 4]),
            ]),
            "ordereddict": OrderedDict([
                ("b", OrderedDict([("b", 1), ("a", 2)])),
                ("a", OrderedDict([("b", 1), ("a", 2)])),
            ]),
        }

    >>> json.dumps(data, pretty=True)
    {
        "bytes": {
            "$builtins.bytes": "SGVsbG8="
        },
        "date": {
            "$datetime.date": "2010-01-01"
        },
        "datetime": {
            "$datetime.datetime": "2020-01-01T18:30:00.000500"
        },
        "deque": {
            "$collections.deque": [
                {
                    "$collections.deque": [
                        1,
                        2
                    ]
                },
                {
                    "$collections.deque": [
                        3,
                        4
                    ]
                }
            ]
        },
        "int": 1,
        "ordereddict": {
            "$collections.OrderedDict": [
                [
                    "b",
                    {
                        "$collections.OrderedDict": [
                            [
                                "b",
                                1
                            ],
                            [
                                "a",
                                2
                            ]
                        ]
                    }
                ],
                [
                    "a",
                    {
                        "$collections.OrderedDict": [
                            [
                                "b",
                                1
                            ],
                            [
                                "a",
                                2
                            ]
                        ]
                    }
                ]
            ]
        },
        "set": {
            "$builtins.set": [
                {
                    "$datetime.datetime": "2000-01-02T00:00:00"
                },
                {
                    "$datetime.datetime": "2000-01-01T00:00:00"
                }
            ]
        },
        "str": "Hello"
    }


Extend
-------------------------------------------------------------------------------
You can extend your Encoder/Decoder in this way:

1. inherit from ``SuperJson``
2. define encode method and decode method in this name convention ``dump_xxx``, ``load_xxx``.
3. dumper method has to dump object to a json serializable dictionary, and use "$<class_name>" as the key.
4. dumper and loader method must have a second argument ``class_name``, it must have a default value equals to the class name you want to support. there's a method ``get_class_name`` can help you to find out what is the correct class name.

Example:

.. code-block:: python

    >>> from pathlib import Path
    >>> from superjson import SuperJson, get_class_name

    >>> class MySuperJson(SuperJson):
    ...     def dump_Path(self, obj, class_name="pathlib.Path"):
    ...         return {"$" + class_name: str(obj.absolute())}
    ...
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
    >>> class_name = get_class_name(p) # this method can help you find your class_name
    >>> s = json.dumps(p)
    >>> s
    {"$pathlib.WindowsPath": "C:\\Users\\shu\\PycharmProjects\\py34\\superjson-project\\tests\\temp.py"}
    >>> p1 = json.loads(s)


Comment
-------------------------------------------------------------------------------
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


Compression
-------------------------------------------------------------------------------
.. code-block:: python

    >>> data = dict(a=1, b=2, c=3)

    # Compress
    >>> s = json.dumps(data, compress=True)

    # Decompress
    >>> data1 = json.loads(s, decompress=True)

    # Auto compress
    >>> json.dump(data, "data.gz")

    # Auto decompress
    >>> json.load("data.gz")


Advance file I/O utility method
-------------------------------------------------------------------------------
If your program is interrupted while writing, you got an incomplete file, and you also lose the original file. To solve this issue, ``json.safe_dump(data, abspath)`` method write json to a temporary file first, then rename to what you expect, and silently overwrite old one. This can guarantee atomic write operation.

.. code-block:: python

    >>> data = dict(a=1, b=2, c=3)
    >>> json.safe_dump(data, "data.gz")


.. _install:

Install
-------------------------------------------------------------------------------

``superjson`` is released on PyPI, so all you need is:

.. code-block:: console

	$ pip install superjson

To upgrade to latest version:

.. code-block:: console

	$ pip install --upgrade superjson