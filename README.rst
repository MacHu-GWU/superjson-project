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

1. **Support** for ``date``, ``datetime``, ``set``, ``OrderedDict``, ``deque``, ``numpy.ndarray``, that the original `json <https://docs.python.org/3/library/json.html>`_ module can not serialize.
2. **Easy to extend to support any custom data type**, `see how <https://superjson.readthedocs.io/index.html#extend>`_.
3. Allow ``// double slash started comments``, ``# Pound key started comments`` style **comment** in json file (Good for human/machine readable config file).
4. Use ``.gz`` for file extension, data will be **automatically compressed**.
5. **Atomic Write is ensured**.


Usage:

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
    ...
    >>> json.dump(data, "data.gz", overwrite=True) # atomic write ensured
    ...


Quick Links
------------------------------------------------------------------------------


- .. image:: https://img.shields.io/badge/Link-Document-red.svg
      :target: https://superjson.readthedocs.io/index.html

- .. image:: https://img.shields.io/badge/Link-API_Reference_and_Source_Code-red.svg
      :target: https://superjson.readthedocs.io/py-modindex.html

- .. image:: https://img.shields.io/badge/Link-Install-red.svg
      :target: `install`_

- .. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
      :target: https://github.com/MacHu-GWU/superjson-project

- .. image:: https://img.shields.io/badge/Link-Submit_Issue_and_Feature_Request-blue.svg
      :target: https://github.com/MacHu-GWU/superjson-project/issues

- .. image:: https://img.shields.io/badge/Link-Download-blue.svg
      :target: https://pypi.python.org/pypi/superjson#downloads


.. _install:

Install
-------------------------------------------------------------------------------

``superjson`` is released on PyPI, so all you need is:

.. code-block:: console

	$ pip install superjson

To upgrade to latest version:

.. code-block:: console

	$ pip install --upgrade superjson