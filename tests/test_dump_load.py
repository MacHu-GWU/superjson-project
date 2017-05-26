#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string
import pytest
from pprint import pprint
from superjson import json
from test_all import data

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


def test():
    """
    """
    json.dump(data, "data1.json", pretty=True)
    data1 = json.load("data1.json")
    assert data == data1

    json.safe_dump(data, "data2.json", pretty=True)
    data2 = json.load("data2.json")
    assert data == data2

    json.dump(data, "data1.gz", pretty=True)
    data1 = json.load("data1.gz")
    assert data == data1

    json.safe_dump(data, "data2.gz", pretty=True)
    data2 = json.load('data2.gz')
    assert data == data2


if __name__ == "__main__":
    import os
    pytest.main([os.path.basename(__file__), "--tb=native", "-s"])
