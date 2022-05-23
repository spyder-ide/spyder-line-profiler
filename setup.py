# -*- coding: utf-8 -*-
#
# Copyright © 2022 Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Setup script for spyder_line_profiler
"""

from setuptools import setup, find_packages
import os
import os.path as osp


def get_version():
    """Get version from source file"""
    import codecs
    with codecs.open("spyder_line_profiler/__init__.py", encoding="utf-8") as f:
        lines = f.read().splitlines()
        for l in lines:
            if "__version__" in l:
                version = l.split("=")[1].strip()
                version = version.replace("'", '').replace('"', '')
                return version


def get_package_data(name, extlist):
    """Return data files for package *name* with extensions in *extlist*"""
    flist = []
    # Workaround to replace os.path.relpath (not available until Python 2.6):
    offset = len(name) + len(os.pathsep)
    for dirpath, _dirnames, filenames in os.walk(name):
        for fname in filenames:
            if not fname.startswith('.') and osp.splitext(fname)[1] in extlist:
                flist.append(osp.join(dirpath, fname)[offset:])
    return flist


# Requirements
REQUIREMENTS = ['line_profiler', 'qtawesome', 'spyder>=5.2']
EXTLIST = ['.jpg', '.png', '.json', '.mo', '.ini']
LIBNAME = 'spyder_line_profiler'


LONG_DESCRIPTION = """
This is a plugin for the Spyder 5 IDE that integrates the Python line profiler.
It allows you to see the time spent in every line.

Usage
-----

Add a ``@profile`` decorator to the functions that you wish to profile
then press Shift+F10 (line profiler default) to run the profiler on
the current script, or go to ``Run > Profile line by line``.

The results will be shown in a dockwidget, grouped by function. Lines
with a stronger color take more time to run.

.. image: https://raw.githubusercontent.com/spyder-ide/spyder-line-profiler/master/img_src/screenshot_profiler.png
"""

setup(
    name=LIBNAME,
    version=get_version(),
    packages=find_packages(),
    package_data={LIBNAME: get_package_data(LIBNAME, EXTLIST)},
    keywords=["Qt PyQt5 PySide2 spyder plugins spyplugins line_profiler profiler"],
    install_requires=REQUIREMENTS,
    url='https://github.com/spyder-ide/spyder-line-profiler',
    license='MIT',
    python_requires='>= 3.7',
    entry_points={
        "spyder.plugins": [
            "spyder_line_profiler = spyder_line_profiler.spyder.plugin:SpyderLineProfiler"
        ],
    },
    author="Spyder Project Contributors",
    description='Plugin for the Spyder 5 IDE that integrates the Python line profiler.',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)'])
