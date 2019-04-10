# -*- coding: utf-8 -*-

import pytest
from superjson import comments

import json


def test_strip_comments():
    s = \
        """
    {
        "a": 1, // this is comment 1
        "b": 2, # this is comment 2
        // this is comment 3
        # this is comment 4
        "c": 3
    }
    """.strip()

    s = comments.strip_comments(s)
    assert json.loads(s) == {"a": 1, "b": 2, "c": 3}


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
