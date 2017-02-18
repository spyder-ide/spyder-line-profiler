#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""

from __future__ import (
    print_function, division, unicode_literals, absolute_import)


@profile
def fact2(n):
    result = 1
    for i in range(2, n + 1):
        result *= i * 2
    return result


def sum2(n):
    result = 0
    for i in range(1, n + 1):
        result += i * 2
    return result

if __name__ == "__main__":
    print(fact2(120))
    print(sum2(120))
