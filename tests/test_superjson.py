# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest
from pytest import raises
from superjson._superjson import (
    is_compressed_json_file,
    superjson as json,
)

import os
from all import data


def abspath_of(basename):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        basename,
    )


def remove_all():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    for basename in os.listdir(test_dir):
        ext = os.path.splitext(basename)[1]
        if ext.lower() in [".json", ".gz"]:
            abspath = os.path.join(test_dir, basename)
            try:
                os.remove(abspath)
            except:
                pass


def setup_module(module):
    remove_all()


def teardown_module(module):
    remove_all()


def test_is_compressed_json_file():
    assert is_compressed_json_file("data.json") is False
    assert is_compressed_json_file("data.js") is False
    assert is_compressed_json_file("data.gz") is True
    with raises(ValueError):
        assert is_compressed_json_file("data.txt") is False


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
            return

    def test_pathlib_path(self):
        try:
            from pathlib import Path
        except ImportError:
            try:
                from pathlib2 import Path
            except:
                return

        data = {
            "a_pathlib_path": Path(__file__)
        }
        s = json.dumps(data, indent=4)
        data1 = json.loads(s)
        assert data == data1
        assert data["a_pathlib_path"].exists()

    def test_pathlib_mate_path(self):
        try:
            from pathlib_mate import PathCls as Path
        except ImportError:
            return

        data = {
            "a_pathlib_mate_path": Path(__file__)
        }
        s = json.dumps(data, indent=4)
        data1 = json.loads(s)
        assert data == data1
        assert data["a_pathlib_mate_path"].exists()


class TestSuperjson(object):
    def test_pretty(self):
        json.dump(data, abspath_of("data1.json"), pretty=True,
                  overwrite=False, verbose=False)
        data1 = json.load(abspath_of("data1.json"), verbose=False)
        assert data == data1

        json.dump(data, abspath_of("data2.json"), pretty=True,
                  overwrite=True, verbose=False)
        data2 = json.load(abspath_of("data2.json"), verbose=False)
        assert data == data2

    def test_auto_compress(self):
        json.dump(data, abspath_of("data1.gz"), pretty=True, verbose=False)
        data1 = json.load(abspath_of("data1.gz"), verbose=False)
        assert data == data1

    def test_overwrite(self):
        json.dump(data, abspath_of("test.json"), overwrite=True, verbose=False)
        json.dump("Hello World!", abspath_of("test.json"), overwrite=True, verbose=False)
        # I don't know why in pytest it doesn't work
        s = json.load(abspath_of("test.json"), verbose=False)
        assert s == "Hello World!"

    def test_load_from_not_exist_file(self):
        with raises(EnvironmentError):
            json.load(abspath_of("not-exists.json"), verbose=False)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
