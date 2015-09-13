spyder.line_profiler
===========================

Description
-----------

This is a plugin to run the python `line profiler <https://github.com/rkern/line_profiler>`_ from within the `spyder <https://code.google.com/p/spyderlib/>`_ editor.

The code is an adaptation of the profiler plugin integrated in `spyder <https://code.google.com/p/spyderlib/>`_.

Install instructions
--------------------

::

  pip install spyder.line_profiler

Usage
-----

Add a ``@profile`` decorator to the functions that you wish to profile then press Shift+F10 (line profiler default) to run the profiler on the current script, or go to ``Run > Profile line by line``.

The results will be shown in a dockwidget, grouped by function. Lines with a stronger color take more time to run.


Screenshot
----------
Line profiler:

.. image:: spyder_line_profiler.png
