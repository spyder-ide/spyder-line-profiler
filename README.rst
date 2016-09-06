spyder.line_profiler
===========================

Description
-----------

This is a plugin to run the python `line profiler <https://github.com/rkern/line_profiler>`_ from within the python IDE `spyder <https://github.com/spyder-ide/spyder>`_.

The code is an adaptation of the profiler plugin integrated in spyder.

Important
---------
**Spyder** plugin support will be released with version 3.0 (Still in Beta).

If you want to try out this plugin you need to use the latest development version of **Spyder**  (**master** branch).


Install instructions
--------------------

See https://github.com/spyder-ide/spyder/wiki/User-plugins, but in short:

::

  pip install spyder.line_profiler

Usage
-----

Add a ``@profile`` decorator to the functions that you wish to profile then press Shift+F10 (line profiler default) to run the profiler on the current script, or go to ``Run > Profile line by line``.

The results will be shown in a dockwidget, grouped by function. Lines with a stronger color take more time to run.


Screenshot
----------
Line profiler:

.. image:: img_src/screenshot_profler.png
