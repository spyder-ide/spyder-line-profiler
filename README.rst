spyder_line_profiler
====================

Description
-----------

This is a plugin to run the python `line profiler <http://pythonhosted.org/line_profiler/>`_ from within the `spyder <https://code.google.com/p/spyderlib/>`_ editor.

The code is an adaptation of the profiler plugin integrated in `spyder <https://code.google.com/p/spyderlib/>`_.

Install instructions
--------------------

Put the files ``p_lineprofiler.py`` and ``widgets/lineprofilergui.py`` in the directory ``spyderplugins/`` from the spyder installation.

For example on Linux this should be ``/usr/lib/python2.7/dist-packages/spyderplugins/`` or equivalent.

The line_profiler module and the kernprof script have to be installed and accessible on the system. See the `official website <http://pythonhosted.org/line_profiler/>`_ for instructions.

Usage
-----

Add a ``@profile`` decorator to the functions that you wish to profile then press Shift+F10 (default) to run the line profiler on the current script or go to ``Execution > Profile line by line``.

The results will be shown in a dockwidget, grouped by function. Lines with a stronger color take more time to run.

Screenshot
----------

.. image:: spyder_line_profiler.png
