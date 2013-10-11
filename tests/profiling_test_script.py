#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""

from __future__ import (
    print_function, division, unicode_literals, absolute_import)


import subdir.profiling_test_script2 as script2


@profile
def fact(n):
    result = 1
    for i in xrange(2, n // 4):
        result *= i
    result = 1
    # This is a comment
    for i in xrange(2, n // 16):
        result *= i
    result = 1

    if False:
        # This won't be run
        raise RuntimeError("What are you doing here ???")

    for i in xrange(2, n + 1):
        result *= i
    return result
    # This is after the end of the function.

    if False:
        # This won't be run
        raise RuntimeError("It's getting bad.")


@profile
def sum_(n):
    result = 0

    for i in xrange(1, n + 1):
        result += i
    return result

if __name__ == "__main__":
    print(fact(120))
    print(sum_(120))
    print(script2.fact2(120))
    print(script2.sum2(120))
