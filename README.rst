spyder_line_profiler
===========================

Project information 
-------------------

.. image:: https://img.shields.io/pypi/l/spyder-line-profiler.svg
   :target: https://github.com/spyder-ide/spyder-line-profiler/blob/master/LICENSE.txt
   
.. image:: https://img.shields.io/pypi/v/spyder-line-profiler.svg
   :target: https://pypi.python.org/pypi/spyder-line-profiler

.. image:: https://badges.gitter.im/spyder-ide/spyder.svg
   :target: https://gitter.im/spyder-ide/public

Build information
-----------------

.. image:: https://ci.appveyor.com/api/projects/status/u8m20qgel4j155pn/branch/master?svg=true
   :target: https://ci.appveyor.com/project/spyder-ide/spyder-line-profiler

.. image:: https://circleci.com/gh/spyder-ide/spyder-line-profiler/tree/master.svg?style=shield
   :target: https://circleci.com/gh/spyder-ide/spyder-line-profiler/tree/master

.. image:: https://coveralls.io/repos/github/spyder-ide/spyder-line-profiler/badge.svg?branch=master
   :target: https://coveralls.io/github/spyder-ide/spyder-line-profiler?branch=master

Description
-----------

This is a plugin to run the python `line profiler <https://github.com/rkern/line_profiler>`_
from within the python IDE `spyder <https://github.com/spyder-ide/spyder>`_.

The code is an adaptation of the profiler plugin integrated in spyder.

Install instructions
--------------------

The line-profiler plugin is available in the ``spyder-ide`` channel in
Anaconda and in PyPI, so it can be installed with the following
commands:

* Using Anaconda: ``conda install -c spyder-ide spyder-line-profiler``
* Using pip: ``pip install spyder-line-profiler``

All dependencies will be automatically installed. You have to restart
Spyder before you can use the plugin.


Usage
-----

Add a ``@profile`` decorator to the functions that you wish to profile then press Shift+F10
(line profiler default) to run the profiler on the current script, or go to
``Run > Profile line by line``.

The results will be shown in a dockwidget, grouped by function. Lines with a stronger color
take more time to run.


Screenshot
----------
Line profiler:

.. image:: img_src/screenshot_profler.png
