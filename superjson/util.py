#!/usr/bin/env python
# -*- coding: utf-8 -*-


def write(s, abspath):
    with open(abspath, "wb") as f:
        f.write(s.encode("utf-8"))


def read(abspath):
    with open(abspath, "rb") as f:
        f.read().decode("utf-8")
