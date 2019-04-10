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


Click `HERE for full documentation <https://superjson.readthedocs.io/index.html>`_.

.. _install:

Install
------------------------------------------------------------------------------

``superjson`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install superjson

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade superjson
