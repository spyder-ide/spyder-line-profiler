# -*- coding: utf-8 -*-
#
# Copyright © 2013 Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

__version__ = '0.1.1'

# =============================================================================
# The following statements are required to register this 3rd party plugin:
# =============================================================================
from .lineprofiler import LineProfiler

PLUGIN_CLASS = LineProfiler
