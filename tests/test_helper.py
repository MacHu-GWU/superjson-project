# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
from superjson.helper import get_class_name


def test_get_class_name():
    import datetime
    import collections

    assert get_class_name(datetime.datetime.now()) == "datetime.datetime"
    assert get_class_name(collections.OrderedDict()) == "collections.OrderedDict"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
