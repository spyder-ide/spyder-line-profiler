# History of changes

## Version 0.3.1 (2022/08/07)

This version fixes a compatibility issue with Spyder 5.3.2 ([Issue 65](https://github.com/spyder-ide/spyder-line-profiler/issues/65), [PR 66](https://github.com/spyder-ide/spyder-line-profiler/pull/66)).


## Version 0.3.0 (2022/06/03)

This version is compatible with Spyder 5.2 and 5.3.

### Issues Closed

* [Issue 54](https://github.com/spyder-ide/spyder-line-profiler/issues/54) - How to proceed with spyder 5 compatibility ([PR 56](https://github.com/spyder-ide/spyder-line-profiler/pull/56) by [@skjerns](https://github.com/skjerns))
* [Issue 52](https://github.com/spyder-ide/spyder-line-profiler/issues/52) - Spyder 5 compatibility ([PR 56](https://github.com/spyder-ide/spyder-line-profiler/pull/56) by [@skjerns](https://github.com/skjerns))
* [Issue 48](https://github.com/spyder-ide/spyder-line-profiler/issues/48) - Correctly register shortcuts
* [Issue 27](https://github.com/spyder-ide/spyder-line-profiler/issues/27) - saving profiling results
* [Issue 25](https://github.com/spyder-ide/spyder-line-profiler/issues/25) - Text box for file to be profiled accept directories

In this release 5 issues were closed.

### Pull Requests Merged

* [PR 62](https://github.com/spyder-ide/spyder-line-profiler/pull/62) - PR: Update `README.md`, `CONTRIBUTING.md`, screenshot and add `RELEASE.md`, by [@dalthviz](https://github.com/dalthviz)
* [PR 61](https://github.com/spyder-ide/spyder-line-profiler/pull/61) - PR: Add default config and change plugin icon, by [@dalthviz](https://github.com/dalthviz)
* [PR 60](https://github.com/spyder-ide/spyder-line-profiler/pull/60) - PR: Remove outdated `conda.recipe` directory, by [@dalthviz](https://github.com/dalthviz)
* [PR 56](https://github.com/spyder-ide/spyder-line-profiler/pull/56) - PR: Switch to new API for Spyder 5, by [@skjerns](https://github.com/skjerns) ([54](https://github.com/spyder-ide/spyder-line-profiler/issues/54), [53](https://github.com/spyder-ide/spyder-line-profiler/issues/53), [52](https://github.com/spyder-ide/spyder-line-profiler/issues/52))

In this release 4 pull requests were closed.


## Version 0.2.1 (2020/04/28)

This release fixes some compatibility issues with Spyder 4.1 and some other bugs.

### Issues Closed

* [Issue 44](https://github.com/spyder-ide/spyder-line-profiler/issues/44) - TextEditor initializer receives unexpected argument size ([PR 46](https://github.com/spyder-ide/spyder-line-profiler/pull/46))
* [Issue 41](https://github.com/spyder-ide/spyder-line-profiler/issues/41) - Move CI to github actions ([PR 45](https://github.com/spyder-ide/spyder-line-profiler/pull/45))
* [Issue 39](https://github.com/spyder-ide/spyder-line-profiler/issues/39) - Crash from opening options ([PR 40](https://github.com/spyder-ide/spyder-line-profiler/pull/40))
* [Issue 35](https://github.com/spyder-ide/spyder-line-profiler/issues/35) - Opening editor from line profiler output is broken ([PR 47](https://github.com/spyder-ide/spyder-line-profiler/pull/47))

In this release 4 issues were closed.

### Pull Requests Merged

* [PR 47](https://github.com/spyder-ide/spyder-line-profiler/pull/47) - PR: Fix opening editor from profiler widget ([35](https://github.com/spyder-ide/spyder-line-profiler/issues/35))
* [PR 46](https://github.com/spyder-ide/spyder-line-profiler/pull/46) - PR: Fix initialization of TextEditor ([44](https://github.com/spyder-ide/spyder-line-profiler/issues/44))
* [PR 45](https://github.com/spyder-ide/spyder-line-profiler/pull/45) - PR: Move CI to GitHub Actions ([41](https://github.com/spyder-ide/spyder-line-profiler/issues/41))
* [PR 43](https://github.com/spyder-ide/spyder-line-profiler/pull/43) - PR: Fix invalid escape sequence in regex string
* [PR 40](https://github.com/spyder-ide/spyder-line-profiler/pull/40) - PR: Add CONF_DEFAULTS ([39](https://github.com/spyder-ide/spyder-line-profiler/issues/39))

In this release 5 pull requests were closed.


## Version 0.2.0 (2019/12/18)

This release updates the plugin to be used with Spyder 4 and fixes some bugs.

### Issues Closed

* [Issue 33](https://github.com/spyder-ide/spyder-line-profiler/issues/33) - Sorting by time / % not working correctly ([PR 38](https://github.com/spyder-ide/spyder-line-profiler/pull/38))
* [Issue 26](https://github.com/spyder-ide/spyder-line-profiler/issues/26) - Update plugin to Spyder v4 ([PR 36](https://github.com/spyder-ide/spyder-line-profiler/pull/36))

In this release 2 issues were closed.

### Pull Requests Merged

* [PR 38](https://github.com/spyder-ide/spyder-line-profiler/pull/38) - PR: Add natural sort for columns ([33](https://github.com/spyder-ide/spyder-line-profiler/issues/33))
* [PR 36](https://github.com/spyder-ide/spyder-line-profiler/pull/36) - PR: Compatibility changes for Spyder 4 ([26](https://github.com/spyder-ide/spyder-line-profiler/issues/26))
* [PR 31](https://github.com/spyder-ide/spyder-line-profiler/pull/31) - PR: Fix continuous integration services
* [PR 30](https://github.com/spyder-ide/spyder-line-profiler/pull/30) - PR: "Profile by line" Button Behavior
* [PR 24](https://github.com/spyder-ide/spyder-line-profiler/pull/24) - Update readme: Plugin can now be installed using conda or pip
* [PR 23](https://github.com/spyder-ide/spyder-line-profiler/pull/23) - Add conda recipe ([15](https://github.com/spyder-ide/spyder-line-profiler/issues/15))

In this release 6 pull requests were closed.


## Version 0.1.1 (2017/03/26)

This version improves the packaging. The code itself was not changed.

### Pull Requests Merged

* [PR 22](https://github.com/spyder-ide/spyder-line-profiler/pull/22) - Install tests alongside package

In this release 1 pull request was closed.


## Version 0.1.0 (2017/03/22)

Initial release.
