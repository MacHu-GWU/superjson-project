#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest
from pytest import raises
from superjson import json
from superjson.pkg.six import PY3

import os
from all import data

file_list = [
    "data1.json", "data2.json", "data3.json",
    "data1.gz", "data2.gz", "data3.gz",
]


def setup_module(module):
    """setup any state specific to the execution of the given module."""
    for path in file_list:
        try:
            os.remove(path)
        except:
            pass


def teardown_module(module):
    """teardown any state that was previously setup with a setup_module
    method.
    """
    for path in file_list:
        try:
            os.remove(path)
        except:
            pass


class Test_dumps_loads(object):
    def test_deal_with_bytes(self):
        b = "Hello".encode("utf-8")
        s = json.dumps(b)
        assert "{" in s
        assert "}" in s
        b1 = json.loads(s, ignore_comments=True)
        assert b == b1

    def test_dumps_pretty(self):
        s = json.dumps(data, pretty=True)
        assert "    " in s
        assert "\n" in s
        data1 = json.loads(s)
        assert data == data1

    def test_float_precision(self):
        data = 3.1415926535
        s = json.dumps(data, float_precision=2)
        assert "3.1415" not in s
        assert "3.14" in s

    def test_ensure_ascii(self):
        data = ["α", "β", "θ"]

        s = json.dumps(data)
        assert "α" not in s
        assert json.loads(s) == data

        s = json.dumps(data, ensure_ascii=False)
        assert "α" in s
        assert json.loads(s) == data

    def test_compress(self):
        data = list(range(1000))
        s1 = json.dumps(data, compress=False)
        s2 = json.dumps(data, compress=True)
        assert len(s1) > len(s2)
        assert json.loads(s2, decompress=True) == data

    def test_numpy(self):
        try:
            import numpy as np
            from datetime import datetime

            data = {
                "ndarray_int": np.array([[1, 2], [3, 4]]),
                "ndarray_float": np.array([[1.1, 2.2], [3.3, 4.4]]),
                "ndarray_str": np.array([["a", "b"], ["c", "d"]]),
                "ndarray_datetime": np.array(
                    [datetime(2000, 1, 1), datetime(2010, 1, 1)]
                ),
            }
            s = json.dumps(data, indent=4)
            data1 = json.loads(s)
            for key in data:
                assert np.array_equal(data[key], data1[key])
        except ImportError:
            pass


class Test_dump_and_safe_dump_and_load(object):
    def test_pretty(self):
        json.dump(data, "data1.json", pretty=True, verbose=False)
        data1 = json.load("data1.json", verbose=False)
        assert data == data1

        json.safe_dump(data, "data2.json", pretty=True, verbose=False)
        data2 = json.load("data2.json", verbose=False)
        assert data == data2

    def test_auto_compress(self):
        json.dump(data, "data1.gz", pretty=True, verbose=False)
        data1 = json.load("data1.gz", verbose=False)
        assert data == data1

        json.safe_dump(data, "data2.gz", pretty=True, verbose=False)
        data2 = json.load("data2.gz", verbose=False)
        assert data == data2

        with raises(ValueError):
            json.safe_dump(data, "data.txt", verbose=False)

    def test_overwrite(self):
        json.dump(data, "test.json", overwrite=False, verbose=False)
        # I don't know why in pytest it doesn't work
        # with open("test.json", "rb") as f:
        #     content = f.read().decode("utf-8")
        #     assert content.startswith("Please")

    def test_not_exists(self):
        with raises(EnvironmentError):
            json.load("not-exists.json", verbose=False)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
