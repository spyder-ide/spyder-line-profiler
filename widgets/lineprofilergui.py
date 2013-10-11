# -*- coding: utf-8 -*-
#
# Copyright © 2011 Santiago Jaramillo
# based on pylintgui.py by Pierre Raybaut
#
# Licensed under the terms of the MIT License
# (see spyderlib/__init__.py for details)

"""
Line Profiler widget

See the official documentation of line_profiler:
http://pythonhosted.org/line_profiler/

Questions for Pierre and others:
    - Where in the menu should line profiler go?  Run > Profile code by line ?
"""

from __future__ import with_statement

from spyderlib.qt.QtGui import (QHBoxLayout, QWidget, QMessageBox, QVBoxLayout,
                                QLabel, QTreeWidget, QTreeWidgetItem,
                                QApplication, QBrush, QColor, QFont)
from spyderlib.qt.QtCore import SIGNAL, QProcess, QByteArray, Qt, QTextCodec
locale_codec = QTextCodec.codecForLocale()
from spyderlib.qt.compat import getopenfilename

import sys
import os
import os.path as osp
import time
import cPickle
import linecache
import inspect

# Local imports
from spyderlib.utils.qthelpers import create_toolbutton, get_icon
from spyderlib.utils.programs import shell_split
from spyderlib.baseconfig import get_conf_path, get_translation
from spyderlib.widgets.texteditor import TextEditor
from spyderlib.widgets.comboboxes import PythonModulesComboBox
from spyderlib.widgets.externalshell import baseshell
from spyderlib.py3compat import to_text_string, getcwd
_ = get_translation("p_lineprofiler", dirname="spyderplugins")


COL_NO = 0
COL_LINE = 5
COL_PERCENT = 4
COL_TIME = 2
COL_PERHIT = 3
COL_HITS = 1
COL_POS = 6


def is_lineprofiler_installed():
    from spyderlib.utils.programs import is_module_installed
    return is_module_installed('line_profiler')


class LineProfilerWidget(QWidget):
    """
    Line profiler widget
    """
    DATAPATH = get_conf_path('lineprofiler.results')
    VERSION = '0.0.1'

    def __init__(self, parent, max_entries=100):
        QWidget.__init__(self, parent)

        self.setWindowTitle("Line profiler")

        self.output = None
        self.error_output = None

        self._last_wdir = None
        self._last_args = None
        self._last_pythonpath = None

        self.filecombo = PythonModulesComboBox(self)

        self.start_button = create_toolbutton(
            self, icon=get_icon('run.png'),
            text=_("Profile by line"),
            tip=_("Run line profiler"),
            triggered=self.start, text_beside_icon=True)
        self.stop_button = create_toolbutton(
            self,
            icon=get_icon('terminate.png'),
            text=_("Stop"),
            tip=_("Stop current profiling"),
            text_beside_icon=True)
        self.connect(self.filecombo, SIGNAL('valid(bool)'),
                     self.start_button.setEnabled)
        #self.connect(self.filecombo, SIGNAL('valid(bool)'), self.show_data)
        # FIXME: The combobox emits this signal on almost any event
        #        triggering show_data() too early, too often.

        browse_button = create_toolbutton(
            self, icon=get_icon('fileopen.png'),
            tip=_('Select Python script'),
            triggered=self.select_file)

        self.datelabel = QLabel()

        self.log_button = create_toolbutton(
            self, icon=get_icon('log.png'),
            text=_("Output"),
            text_beside_icon=True,
            tip=_("Show program's output"),
            triggered=self.show_log)

        self.datatree = LineProfilerDataTree(self)

        self.collapse_button = create_toolbutton(
            self,
            icon=get_icon('collapse.png'),
            triggered=lambda dD=-1: self.datatree.collapseAll(),
            tip=_('Collapse all'))
        self.expand_button = create_toolbutton(
            self,
            icon=get_icon('expand.png'),
            triggered=lambda dD=1: self.datatree.expandAll(),
            tip=_('Expand all'))

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.filecombo)
        hlayout1.addWidget(browse_button)
        hlayout1.addWidget(self.start_button)
        hlayout1.addWidget(self.stop_button)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.collapse_button)
        hlayout2.addWidget(self.expand_button)
        hlayout2.addStretch()
        hlayout2.addWidget(self.datelabel)
        hlayout2.addStretch()
        hlayout2.addWidget(self.log_button)

        layout = QVBoxLayout()
        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addWidget(self.datatree)
        self.setLayout(layout)

        self.process = None
        self.set_running_state(False)
        self.start_button.setEnabled(False)

        if not is_lineprofiler_installed():
            # This should happen only on certain GNU/Linux distributions
            # or when this a home-made Python build because the Python
            # profilers are included in the Python standard library
            for widget in (self.datatree, self.filecombo,
                           self.start_button, self.stop_button):
                widget.setDisabled(True)
            url = 'http://docs.python.org/library/profile.html'
            text = '%s <a href=%s>%s</a>' % (_('Please install'), url,
                                             _("the Python profiler modules"))
            self.datelabel.setText(text)
        else:
            pass  # self.show_data()

    def analyze(self, filename, wdir=None, args=None, pythonpath=None):
        if not is_lineprofiler_installed():
            return
        self.kill_if_running()
        #index, _data = self.get_data(filename)
        index = None  # FIXME: storing data is not implemented yet
        if index is None:
            self.filecombo.addItem(filename)
            self.filecombo.setCurrentIndex(self.filecombo.count()-1)
        else:
            self.filecombo.setCurrentIndex(self.filecombo.findText(filename))
        self.filecombo.selected()
        if self.filecombo.is_valid():
            if wdir is None:
                wdir = osp.dirname(filename)
            self.start(wdir, args, pythonpath)

    def select_file(self):
        self.emit(SIGNAL('redirect_stdio(bool)'), False)
        filename, _selfilter = getopenfilename(
            self, _("Select Python script"), getcwd(),
            _("Python scripts")+" (*.py ; *.pyw)")
        self.emit(SIGNAL('redirect_stdio(bool)'), False)
        if filename:
            self.analyze(filename)

    def show_log(self):
        if self.output:
            TextEditor(self.output, title=_("Line profiler output"),
                       readonly=True, size=(700, 500)).exec_()

    def show_errorlog(self):
        if self.error_output:
            TextEditor(self.error_output, title=_("Line profiler output"),
                       readonly=True, size=(700, 500)).exec_()

    def start(self, wdir=None, args=None, pythonpath=None):
        filename = to_text_string(self.filecombo.currentText())
        if wdir is None:
            wdir = self._last_wdir
            if wdir is None:
                wdir = osp.basename(filename)
        if args is None:
            args = self._last_args
            if args is None:
                args = []
        if pythonpath is None:
            pythonpath = self._last_pythonpath
        self._last_wdir = wdir
        self._last_args = args
        self._last_pythonpath = pythonpath

        self.datelabel.setText(_('Profiling, please wait...'))

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.SeparateChannels)
        self.process.setWorkingDirectory(wdir)
        self.connect(self.process, SIGNAL("readyReadStandardOutput()"),
                     self.read_output)
        self.connect(self.process, SIGNAL("readyReadStandardError()"),
                     lambda: self.read_output(error=True))
        self.connect(self.process,
                     SIGNAL("finished(int,QProcess::ExitStatus)"),
                     self.finished)
        self.connect(self.stop_button, SIGNAL("clicked()"), self.process.kill)

        if pythonpath is not None:
            env = [to_text_string(_pth)
                   for _pth in self.process.systemEnvironment()]
            baseshell.add_pathlist_to_PYTHONPATH(env, pythonpath)
            self.process.setEnvironment(env)

        self.output = ''
        self.error_output = ''

        if os.name == 'nt':
            # On Windows, one has to replace backslashes by slashes to avoid
            # confusion with escape characters (otherwise, for example, '\t'
            # will be interpreted as a tabulation):
            filename = osp.normpath(filename).replace(os.sep, '/')
        executable = "kernprof.py"
        p_args = ['-lvb', '-o', self.DATAPATH, filename]
        if args:
            p_args.extend(shell_split(args))
        self.process.start(executable, p_args)

        running = self.process.waitForStarted()
        self.set_running_state(running)
        if not running:
            QMessageBox.critical(self, _("Error"),
                                 _("Process failed to start"))

    def set_running_state(self, state=True):
        self.start_button.setEnabled(not state)
        self.stop_button.setEnabled(state)

    def read_output(self, error=False):
        if error:
            self.process.setReadChannel(QProcess.StandardError)
        else:
            self.process.setReadChannel(QProcess.StandardOutput)
        qba = QByteArray()
        while self.process.bytesAvailable():
            if error:
                qba += self.process.readAllStandardError()
            else:
                qba += self.process.readAllStandardOutput()
        text = to_text_string(locale_codec.toUnicode(qba.data()))
        if error:
            self.error_output += text
        else:
            self.output += text

    def finished(self):
        self.set_running_state(False)
        self.show_errorlog()  # If errors occurred, show them.
        self.output = self.error_output + self.output
        # FIXME: figure out if show_data should be called here or
        #        as a signal from the combobox
        self.show_data(justanalyzed=True)

    def kill_if_running(self):
        if self.process is not None:
            if self.process.state() == QProcess.Running:
                self.process.kill()
                self.process.waitForFinished()

    def show_data(self, justanalyzed=False):
        if not justanalyzed:
            self.output = None
        self.log_button.setEnabled(
            self.output is not None and len(self.output) > 0)
        self.kill_if_running()
        filename = to_text_string(self.filecombo.currentText())
        if not filename:
            return

        self.datatree.load_data(self.DATAPATH)
        self.datelabel.setText(_('Sorting data, please wait...'))
        QApplication.processEvents()
        self.datatree.show_tree()

        text_style = "<span style=\'color: #444444\'><b>%s </b></span>"
        date_text = text_style % time.strftime("%d %b %Y %H:%M",
                                               time.localtime())
        self.datelabel.setText(date_text)


class LineProfilerDataTree(QTreeWidget):
    """
    Convenience tree widget (with built-in model)
    to store and view line profiler data.

    The quantities calculated by the line profiler are as follows
    (from profile.Profile):
    [0] = The number of times this function was called, not counting direct
          or indirect recursion,
    [1] = Number of times this function appears on the stack, minus one
    [2] = Total time spent internal to this function
    [3] = Cumulative time that this function was present on the stack.  In
          non-recursive functions, this is the total execution time from start
          to finish of each invocation of a function, including time spent in
          all subfunctions.
    [4] = A dictionary indicating for each function name, the number of times
          it was called by us.
    """
    SEP = r"<[=]>"  # separator between filename and linenumber
    # (must be improbable as a filename to avoid splitting the filename itself)

    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.header_list = [
            _('Line #'), _('Hits'), _('Time (ms)'), _('Per hit (ms)'),
            _('% Time'), _('Line contents'), _('File:line')]
        self.stats = None      # To be filled by self.load_data()
        self.max_time = 0      # To be filled by self.load_data()
        self.header().setDefaultAlignment(Qt.AlignCenter)
        self.setColumnCount(len(self.header_list))
        self.setHeaderLabels(self.header_list)
        self.setColumnHidden(self.columnCount()-1, True)
        self.clear()
        self.connect(self, SIGNAL('itemActivated(QTreeWidgetItem*,int)'),
                     self.item_activated)

    def get_item_data(self, item):
        """Get tree item user data: (filename, line_no)"""
        filename, line_no_str = str(item.text(COL_POS)).rsplit(":", 1)
        return filename, int(line_no_str)

    def load_data(self, profdatafile):
        """Load line profiler data saved by kernprof.py module"""
        # lstats has the following layout :
        # lstats.timings =
        #     {(filename1, line_no1, function_name1):
        #         [(line_no1, hits1, total_time1),
        #          (line_no2, hits2, total_time2)],
        #      (filename2, line_no2, function_name2):
        #         [(line_no1, hits1, total_time1),
        #          (line_no2, hits2, total_time2),
        #          (line_no3, hits3, total_time3)]}
        # lstats.unit = time_factor
        with open(profdatafile, 'rb') as fid:
            lstats = cPickle.load(fid)

        # First pass to group by filename
        self.stats = dict()
        linecache.checkcache()
        for func_info, stats in lstats.timings.iteritems():
            # func_info is a tuple containing (filename, line, function anme)
            filename, start_line_no, func_name = func_info
            filename = filename.decode('utf8')

            # Read code
            start_line_no -= 1  # include the @profile decorator
            all_lines = linecache.getlines(filename)
            block_lines = inspect.getblock(all_lines[start_line_no-1:])

            # Loop on each line of code
            func_stats = []
            func_total_time = 0.0
            next_stat_line = 0
            func_max_time = 0.0
            for line_no, code_line in enumerate(block_lines):
                line_no += start_line_no
                code_line = code_line.rstrip('\n').decode('utf8')
                if (next_stat_line < len(stats)
                        and line_no != stats[next_stat_line][0]):
                    # Line didn't run
                    hits, line_total_time, time_per_hit = None, None, None
                else:
                    # Compute line times
                    hits, line_total_time = stats[next_stat_line][1:]
                    line_total_time *= lstats.unit
                    time_per_hit = line_total_time / hits
                    func_total_time += line_total_time
                    next_stat_line += 1
                    func_max_time = max(func_max_time, line_total_time)
                func_stats.append(
                    [line_no, code_line, line_total_time, time_per_hit,
                     hits])

            # Compute percent time
            for line in func_stats:
                line_total_time = line[2]
                if line_total_time is None:
                    line.append(None)
                else:
                    line.append(line_total_time / func_total_time)

            # Fill dict
            self.stats[func_info] = [func_stats, func_total_time,
                                     func_max_time]

    def show_tree(self):
        """Populate the tree with line profiler data and display it."""
        self.clear()  # Clear before re-populating
        self.setItemsExpandable(True)
        self.setSortingEnabled(False)
        self.populate_tree()
        self.expandAll()
        for col in range(self.columnCount()-1):
            self.resizeColumnToContents(col)
        self.collapseAll()
        self.setSortingEnabled(True)
        self.sortItems(COL_POS, Qt.AscendingOrder)

    def fill_item(self, item, filename, line_no, code, time, percent, perhit,
                  hits):
            item.setData(COL_POS, Qt.DisplayRole,
                         '%s:%s' % (osp.normpath(filename), line_no))

            item.setData(COL_NO, Qt.DisplayRole, line_no)

            item.setData(COL_LINE, Qt.DisplayRole, code)

            if percent is None:
                percent = ''
            elif isinstance(percent, (int, long, float)):
                percent = '%.1f' % (100 * percent)
            item.setData(COL_PERCENT, Qt.DisplayRole, percent)
            item.setTextAlignment(COL_PERCENT, Qt.AlignCenter)

            if time is None:
                time = ''
            elif isinstance(time, (int, long, float)):
                time = '%.3f' % (time * 1e3)
            item.setData(COL_TIME, Qt.DisplayRole, time)
            item.setTextAlignment(COL_TIME, Qt.AlignCenter)

            if perhit is None:
                perhit = ''
            elif isinstance(perhit, (int, long, float)):
                perhit = '%.3f' % (perhit * 1e3)
            item.setData(COL_PERHIT, Qt.DisplayRole, perhit)
            item.setTextAlignment(COL_PERHIT, Qt.AlignCenter)

            if hits is None:
                hits = ''
            elif isinstance(hits, (int, long, float)):
                hits = '%d' % hits
            item.setData(COL_HITS, Qt.DisplayRole, hits)
            item.setTextAlignment(COL_HITS, Qt.AlignCenter)

    def populate_tree(self):
        """Create each item (and associated data) in the tree"""
        try:
            monospace_font = self.window().editor.get_plugin_font()
        except AttributeError:  # If run standalone for testing
            monospace_font = QFont("Courier New")
            monospace_font.setPointSize(10)

        for func_info, func_data in self.stats.iteritems():
            # Function name and position
            filename, start_line_no, func_name = func_info
            func_stats, func_total_time, func_max_time = func_data
            func_item = QTreeWidgetItem(self)
            func_item.setData(
                0, Qt.DisplayRole,
                _('{func_name} ({time_ms:.3f}ms) in file "{filename}", '
                  'line {line_no}').format(
                    filename=func_info[0],
                    line_no=func_info[1],
                    func_name=func_info[2],
                    time_ms=func_total_time * 1e3))
            # For sorting by time
            func_item.setData(COL_TIME, Qt.DisplayRole, func_total_time * 1e3)
            func_item.setData(COL_PERCENT, Qt.DisplayRole,
                              func_total_time * 1e3)
            func_item.setFirstColumnSpanned(True)

            # Lines of code
            for line_info in func_stats:
                line_item = QTreeWidgetItem(func_item)
                (line_no, code_line, line_total_time, time_per_hit,
                 hits, percent) = line_info
                self.fill_item(
                    line_item, filename, line_no, code_line,
                    line_total_time, percent, time_per_hit, hits)

                # Color background
                if line_total_time is not None:
                    alpha = line_total_time / func_max_time
                    color = QBrush(QColor.fromRgbF(1, 0, 0, alpha))
                    for col in range(self.columnCount()):
                        line_item.setBackground(col, color)

                # Monospace font for code
                line_item.setFont(COL_LINE, monospace_font)

    def item_activated(self, item):
        filename, line_no = self.get_item_data(item)
        self.parent().emit(SIGNAL("edit_goto(QString,int,QString)"),
                           filename, line_no, '')
        print(filename, line_no)


def test():
    """Run widget test"""
    from spyderlib.utils.qthelpers import qapplication
    app = qapplication()
    widget = LineProfilerWidget(None)
    widget.resize(800, 600)
    widget.show()
    widget.analyze(osp.normpath(osp.join(osp.dirname(__file__), os.pardir,
                                         'tests/profiling_test_script.py')))
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
