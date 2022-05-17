# -*- coding: utf-8 -*-
#
# Copyright © 2017 Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""Tests for lineprofiler.py."""

# Standard library imports
import os

# Third party imports
from qtpy.QtCore import Qt
from unittest.mock import Mock

# Local imports
from spyder_line_profiler.spyder.widgets import SpyderLineProfilerWidget


TEST_SCRIPT = \
"""import time
@profile
def foo():
    time.sleep(1)
    xs = []
    for k in range(100):
        xs = xs + ['x']
foo()"""

        
def test_profile_and_display_results(qtbot, tmpdir):
    """Run profiler on simple script and check that results are okay."""
    os.chdir(tmpdir.strpath)
    testfilename = tmpdir.join('test_foo.py').strpath

    with open(testfilename, 'w') as f:
        f.write(TEST_SCRIPT)

    MockQMessageBox = Mock()

    widget = SpyderLineProfilerWidget(None)
    widget.setup()
    qtbot.addWidget(widget)
    with qtbot.waitSignal(widget.sig_finished, timeout=10000, raising=True):
        widget.analyze(testfilename)

    MockQMessageBox.assert_not_called()
    dt = widget.datatree
    assert dt.topLevelItemCount() == 1  # number of functions profiled
    
    top = dt.topLevelItem(0)                               
    assert top.data(0, Qt.DisplayRole).startswith('foo ')
    assert top.childCount() == 6
    for i in range(6):
        assert top.child(i).data(0, Qt.DisplayRole) == i + 2  # line no

    assert top.child(2).data(1, Qt.DisplayRole) == '1'  # hits
    assert top.child(3).data(1, Qt.DisplayRole) == '1' 
    assert top.child(4).data(1, Qt.DisplayRole) == '101'
    assert top.child(5).data(1, Qt.DisplayRole) == '100'

    assert float(top.child(2).data(2, Qt.DisplayRole)) >= 900  # time (ms)
    assert float(top.child(2).data(2, Qt.DisplayRole)) <= 1200
    assert float(top.child(3).data(2, Qt.DisplayRole)) <= 100
    assert float(top.child(4).data(2, Qt.DisplayRole)) <= 100
    assert float(top.child(5).data(2, Qt.DisplayRole)) <= 100
