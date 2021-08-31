# -*- coding: utf-8 -*-
#
# Copyright © 2013 Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Setup script for spyder_line_profiler
"""

from setuptools import setup, find_packages
import os
import os.path as osp


def get_version(LIBNAME):
    """Get version from source file"""
    import codecs
    with codecs.open(LIBNAME + "/__init__.py", encoding="utf-8") as f:
        lines = f.read().splitlines()
        for l in lines:
            if "__version__" in l:
                version = l.split("=")[1].strip()
                version = version.replace("'", '').replace('"', '')
                return version
            
def spyder5_installed():
    """Get spyder version"""
    import spyder
    return int(spyder.__version__[0]) > 4

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
REQUIREMENTS = ['line_profiler', 'spyder>=4']
EXTLIST = ['.jpg', '.png', '.json', '.mo', '.ini']
LIBNAME = 'spyder_line_profiler' + ("_5" if spyder5_installed() else "")


LONG_DESCRIPTION = """
This is a plugin for the Spyder IDE that integrates the Python line profiler.
It allows you to see the time spent in every line.

Usage
-----

Add a ``@profile`` decorator to the functions that you wish to profile
then press Shift+F10 (line profiler default) to run the profiler on
the current script, or go to ``Run > Profile line by line``.

The results will be shown in a dockwidget, grouped by function. Lines
with a stronger color take more time to run.

.. image: https://raw.githubusercontent.com/spyder-ide/spyder-line-profiler/master/img_src/screenshot_profler.png
"""


setup(
    name=LIBNAME,
    version=get_version(LIBNAME),
    packages=find_packages(),
    package_data={LIBNAME: get_package_data(LIBNAME, EXTLIST)},
    description="Plugin for the Spyder IDE that integrates the Python line profiler.",
    install_requires=REQUIREMENTS,
    url="https://github.com/skjerns/spyder-line-profiler",
    license="MIT",
    python_requires='>= 3.7',
    entry_points={
        "spyder.plugins": [
            "spyder_line_profiler_5 = spyder_line_profiler_5.spyder.plugin:SpyderLineProfiler5"
        ],
    } if spyder5_installed() else {},
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt',
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)'
        ]
)
