# Contributing to the Spyder line profiler plugin

:+1::tada: 
First off, thanks for taking the time to contribute to the Spyder Line Profiler
plugin! 
:tada::+1:

## General guidelines for contributing

The Spyder line profiler plugin is developed as part of the wider Spyder project.
In general, the guidelines for contributing to Spyder also apply here.
Specifically, all contributors are expected to abide by
[Spyder's Code of Conduct](https://github.com/spyder-ide/spyder/blob/master/CODE_OF_CONDUCT.md).

There are many ways to contribute and all are valued and welcome. 
You can help other users, write documentation, spread the word, submit
helpful issues on the
[issue tracker](https://github.com/spyder-ide/spyder-line-profiler/issues)
with problems you encounter or ways to improve the plugin, test the development
version, or submit a pull request on GitHub.

The rest of this document explains how to set up a development environment.

## Setting up a development environment

This section explains how to set up a conda environment to run and work on the
development version of the Spyder line profiler plugin.

### Creating a conda environment

This creates a new conda environment with the name `spyderlp-dev`.

```bash
$ conda create -n spyderlp-dev -c conda-forge python=3.9
$ conda activate spyderlp-dev
```

### Cloning the repository

This creates a new directory `spyder-line-profiler` with the source code of the
Spyder line profiler plugin.

```bash
$ git clone https://github.com/spyder-ide/spyder-line-profiler.git
$ cd spyder-line-profiler
```

### Installing dependencies

This installs Spyder, line_profiler and all other plugin dependencies into
the conda environment previously created, using the conda-forge channel.

```bash
$ conda install -c conda-forge --file requirements/conda.txt
```

### Installing the plugin

This installs the Spyder line profiler plugin so that Spyder will use it.

```bash
$ pip install --no-deps -e .
```

### Running Spyder

You are done! You can run Spyder as normal and it should load the line profiler
plugin.

```bash
$ spyder
```

### Running Tests

This command installs the test dependencies into your conda environment, using the conda-forge channel.

```bash
$ conda install -c conda-forge --file requirements/tests.txt
```

You can now run the tests with a simple

```bash
$ pytest
```
 
