# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2021, Spyder Line Profiler contributors
#
# Licensed under the terms of the MIT license
# ----------------------------------------------------------------------------
"""
Spyder Line Profiler 5 Main Widget.
"""
# Standard library imports
from __future__ import with_statement
import hashlib
import inspect
import linecache
import re
import os
import os.path as osp
import time

# Third party imports
from qtpy.QtWidgets import QHBoxLayout, QLabel
from qtpy.QtGui import QBrush, QColor, QFont
from qtpy.QtCore import (QByteArray, QProcess, Qt, QTextCodec,
                         QProcessEnvironment, Signal)
from qtpy.QtWidgets import (QMessageBox, QVBoxLayout,
                            QTreeWidget, QTreeWidgetItem, QApplication)
from qtpy.compat import getopenfilename
from spyder.plugins.variableexplorer.widgets.texteditor import TextEditor

# Spyder imports
from spyder.api.config.decorators import on_conf_change
from spyder.api.translations import get_translation
from spyder.config.base import get_conf_path

from spyder.api.widgets.main_widget import PluginMainWidget
from spyder.widgets.comboboxes import PythonModulesComboBox
from spyder.utils.qthelpers import create_toolbutton
from spyder.utils import programs
from spyder.utils.misc import add_pathlist_to_PYTHONPATH, getcwd_or_home
from spyder.plugins.run.widgets import get_run_configuration
from spyder.py3compat import to_text_string, getcwd, pickle

# Localization
_ = get_translation("spyder_line_profiler.spyder")


COL_NO = 0
COL_HITS = 1
COL_TIME = 2
COL_PERHIT = 3
COL_PERCENT = 4
COL_LINE = 5
COL_POS = 0  # Position is not displayed but set as Qt.UserRole

CODE_NOT_RUN_COLOR = QBrush(QColor.fromRgb(128, 128, 128, 200))

WEBSITE_URL = 'http://pythonhosted.org/line_profiler/'

locale_codec = QTextCodec.codecForLocale()


# This is needed for testing this module as a stand alone script
try:
    _ = get_translation("line_profiler", dirname="spyder_line_profiler")
except KeyError as error:
    import gettext
    _ = gettext.gettext



def is_lineprofiler_installed():
    """
    Checks if the program and the library for line_profiler is installed.
    """
    return (programs.is_module_installed('line_profiler')
            and programs.find_program('kernprof') is not None)


    
class TreeWidgetItem(QTreeWidgetItem):
    """
    An extension of QTreeWidgetItem that replaces the sorting behaviour
    such that the sorting is not purely by ASCII index but by natural
    sorting, e.g. multi-digit numbers sorted based on their value instead
    of individual digits.

    Taken from
    https://stackoverflow.com/questions/21030719/sort-a-pyside-qtgui-
    qtreewidget-by-an-alpha-numeric-column/
    """
    def __lt__(self, other):
        """
        Compare a widget text entry to another entry.
        """
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        return self.natural_sort_key(key1) < self.natural_sort_key(key2)

    @staticmethod
    def natural_sort_key(key):
        """
        Natural sorting for both numbers and strings containing numbers.
        """
        regex = r'(\d*\.\d+|\d+)'
        parts = re.split(regex, key)
        return tuple((e if i % 2 == 0 else float(e))
                     for i, e in enumerate(parts))




class SpyderLineProfilerWidget(PluginMainWidget):

    # PluginMainWidget class constants
    DATAPATH = get_conf_path('lineprofiler.results')
    VERSION = '0.0.1'
    redirect_stdio = Signal(bool)
    sig_finished = Signal()
    # Signals
    sig_edit_goto_requested = Signal(str, int, str)
    """
    This signal will request to open a file in a given row and column
    using a code editor.
    
    Parameters
    ----------
    path: str
        Path to file.
    row: int
        Cursor starting row position.
    word: str
        Word to select on given row.
    """

    def __init__(self, name=None, plugin=None, parent=None):
        super().__init__(name, plugin, parent)


        self.spyder_pythonpath = None

        self.setWindowTitle("Line profiler")

        self.output = None
        self.error_output = None

        self.use_colors = True

        self._last_wdir = None
        self._last_args = None
        self._last_pythonpath = None

        self.filecombo = PythonModulesComboBox(self)

        self.start_button = create_toolbutton(
            self, icon='run',
            text=_("Profile by line"),
            tip=_("Run line profiler"),
            triggered=(lambda checked=False: self.analyze()), text_beside_icon=True)
        self.stop_button = create_toolbutton(
            self,
            icon='stop',
            text=_("Stop"),
            tip=_("Stop current profiling"),
            text_beside_icon=True)
        self.filecombo.valid.connect(self.start_button.setEnabled)
        #self.filecombo.valid.connect(self.show_data)
        # FIXME: The combobox emits this signal on almost any event
        #        triggering show_data() too early, too often.

        browse_button = create_toolbutton(
            self, icon='fileopen',
            tip=_('Select Python script'),
            triggered=self.select_file)

        self.datelabel = QLabel()

        self.log_button = create_toolbutton(
            self, icon='history',
            text=_("Output"),
            text_beside_icon=True,
            tip=_("Show program's output"),
            triggered=self.show_log)

        self.datatree = LineProfilerDataTree(self)

        self.collapse_button = create_toolbutton(
            self,
            icon='collapse',
            triggered=lambda dD=-1: self.datatree.collapseAll(),
            tip=_('Collapse all'))
        self.expand_button = create_toolbutton(
            self,
            icon='expand',
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
        
        # Signals
        self.datatree.sig_edit_goto_requested.connect(
            self.sig_edit_goto_requested)
        
        if not is_lineprofiler_installed():
            for widget in (self.datatree, self.filecombo, self.log_button,
                           self.start_button, self.stop_button, browse_button,
                           self.collapse_button, self.expand_button):
                widget.setDisabled(True)
            text = _(
                '<b>Please install the <a href="%s">line_profiler module</a></b>'
                ) % WEBSITE_URL
            self.datelabel.setText(text)
            self.datelabel.setOpenExternalLinks(True)
        else:
            pass  # self.show_data()

    # --- PluginMainWidget API
    # ------------------------------------------------------------------------
    def get_title(self):
        return _("Line Profiler")

    def get_focus_widget(self):
        pass

    def setup(self):
        pass

        
    def analyze(self, filename=None, wdir=None, args=None, pythonpath=None,
                use_colors=True):
        self.use_colors = use_colors
        if not is_lineprofiler_installed():
            return
        self.kill_if_running()
        #index, _data = self.get_data(filename) # FIXME: storing data is not implemented yet
        if filename is not None:
            filename = osp.abspath(to_text_string(filename))
            index = self.filecombo.findText(filename)
            if index == -1:
                self.filecombo.addItem(filename)
                self.filecombo.setCurrentIndex(self.filecombo.count()-1)
            else:
                self.filecombo.setCurrentIndex(index)
            self.filecombo.selected()
            
        if self.filecombo.is_valid():
            filename = to_text_string(self.filecombo.currentText())
            runconf = get_run_configuration(filename)
            if runconf is not None:
                if wdir is None:
                    if runconf.wdir_enabled:
                        wdir = runconf.wdir
                    elif runconf.cw_dir:
                        wdir = os.getcwd()
                    elif runconf.file_dir:
                        wdir = osp.dirname(filename)
                    elif runconf.fixed_dir:
                        wdir = runconf.dir
                if args is None:
                    if runconf.args_enabled:
                        args = runconf.args
            if wdir is None:
                wdir = osp.dirname(filename)
            if pythonpath is None:
                pythonpath = self.spyder_pythonpath
            self.start(wdir, args, pythonpath)

    def select_file(self):
        self.redirect_stdio.emit(False)
        try:    
            curr_script = self.editor.get_current_filename()
        except:
            curr_script = None
            
        pwd = curr_script if curr_script else getcwd_or_home()
        
        filename, _selfilter = getopenfilename(
            self, _("Select Python script"), pwd,
            _("Python scripts")+" (*.py ; *.pyw)")
        self.redirect_stdio.emit(False)
        if filename:
            self.analyze(filename)

    def show_log(self):
        if self.output:
            editor = TextEditor(self.output, title=_("Line profiler output"),
                                readonly=True)
            # Call .show() to dynamically resize editor;
            # see spyder-ide/spyder#12202
            editor.show()
            editor.exec_()

    def show_errorlog(self):
        if self.error_output:
            editor = TextEditor(self.error_output,
                                title=_("Line profiler output"),
                                readonly=True)
            # Call .show() to dynamically resize editor;
            # see spyder-ide/spyder#12202
            editor.show()
            editor.exec_()

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
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(
            lambda: self.read_output(error=True))
        self.process.finished.connect(self.finished)
        self.stop_button.clicked.connect(self.process.kill)

        if pythonpath is not None:
            env = [to_text_string(_pth)
                   for _pth in self.process.systemEnvironment()]
            add_pathlist_to_PYTHONPATH(env, pythonpath)
            processEnvironment = QProcessEnvironment()
            for envItem in env:
                envName, separator, envValue = envItem.partition('=')
                processEnvironment.insert(envName, envValue)
            self.process.setProcessEnvironment(processEnvironment)

        self.output = ''
        self.error_output = ''

        if os.name == 'nt':
            # On Windows, one has to replace backslashes by slashes to avoid
            # confusion with escape characters (otherwise, for example, '\t'
            # will be interpreted as a tabulation):
            filename = osp.normpath(filename).replace(os.sep, '/')
            p_args = ['-lvb', '-o', '"' + self.DATAPATH + '"',
                      '"' + filename + '"']
            if args:
                p_args.extend(programs.shell_split(args))
            executable = '"' + programs.find_program('kernprof') + '"'
            executable += ' ' + ' '.join(p_args)
            executable = executable.replace(os.sep, '/')
            self.process.start(executable)
        else:
            p_args = ['-lvb', '-o', self.DATAPATH, filename]
            if args:
                p_args.extend(programs.shell_split(args))
            executable = 'kernprof'
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
        self.sig_finished.emit()

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
    def update_actions(self):
        pass

    @on_conf_change
    def on_section_conf_change(self, section):
        pass


    
    
class LineProfilerDataTree(QTreeWidget):
    """
    Convenience tree widget (with built-in model)
    to store and view line profiler data.
    """
    sig_edit_goto_requested = Signal(str, int, str)
    
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.header_list = [
            _('Line #'), _('Hits'), _('Time (ms)'), _('Per hit (ms)'),
            _('% Time'), _('Line contents')]
        self.stats = None      # To be filled by self.load_data()
        self.max_time = 0      # To be filled by self.load_data()
        self.header().setDefaultAlignment(Qt.AlignCenter)
        self.setColumnCount(len(self.header_list))
        self.setHeaderLabels(self.header_list)
        self.clear()
        self.itemClicked.connect(self.onItemClick)

    def show_tree(self):
        """Populate the tree with line profiler data and display it."""
        self.clear()  # Clear before re-populating
        self.setItemsExpandable(True)
        self.setSortingEnabled(False)
        self.populate_tree()
        self.expandAll()
        for col in range(self.columnCount()-1):
            self.resizeColumnToContents(col)
        if self.topLevelItemCount() > 1:
            self.collapseAll()
        self.setSortingEnabled(True)
        self.sortItems(COL_POS, Qt.AscendingOrder)

    def load_data(self, profdatafile):
        """Load line profiler data saved by kernprof module"""
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
            lstats = pickle.load(fid)

        # First pass to group by filename
        self.stats = dict()
        linecache.checkcache()
        for func_info, stats in lstats.timings.items():
            # func_info is a tuple containing (filename, line, function anme)
            filename, start_line_no = func_info[:2]

            # Read code
            start_line_no -= 1  # include the @profile decorator
            all_lines = linecache.getlines(filename)
            block_lines = inspect.getblock(all_lines[start_line_no:])

            # Loop on each line of code
            func_stats = []
            func_total_time = 0.0
            next_stat_line = 0
            for line_no, code_line in enumerate(block_lines):
                line_no += start_line_no + 1  # Lines start at 1
                code_line = code_line.rstrip('\n')
                if (next_stat_line >= len(stats)
                        or line_no != stats[next_stat_line][0]):
                    # Line didn't run
                    hits, line_total_time, time_per_hit = None, None, None
                else:
                    # Compute line times
                    hits, line_total_time = stats[next_stat_line][1:]
                    line_total_time *= lstats.unit
                    time_per_hit = line_total_time / hits
                    func_total_time += line_total_time
                    next_stat_line += 1
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
            self.stats[func_info] = [func_stats, func_total_time]

    def fill_item(self, item, filename, line_no, code, time, percent, perhit,
                  hits):
        item.setData(COL_POS, Qt.UserRole, (osp.normpath(filename), line_no))

        item.setData(COL_NO, Qt.DisplayRole, line_no)

        item.setData(COL_LINE, Qt.DisplayRole, code)

        if percent is None:
            percent = ''
        else:
            percent = '%.1f' % (100 * percent)
        item.setData(COL_PERCENT, Qt.DisplayRole, percent)
        item.setTextAlignment(COL_PERCENT, Qt.AlignCenter)

        if time is None:
            time = ''
        else:
            time = '%.3f' % (time * 1e3)
        item.setData(COL_TIME, Qt.DisplayRole, time)
        item.setTextAlignment(COL_TIME, Qt.AlignCenter)

        if perhit is None:
            perhit = ''
        else:
            perhit = '%.3f' % (perhit * 1e3)
        item.setData(COL_PERHIT, Qt.DisplayRole, perhit)
        item.setTextAlignment(COL_PERHIT, Qt.AlignCenter)

        if hits is None:
            hits = ''
        else:
            hits = '%d' % hits
        item.setData(COL_HITS, Qt.DisplayRole, hits)
        item.setTextAlignment(COL_HITS, Qt.AlignCenter)

    def populate_tree(self):
        """Create each item (and associated data) in the tree"""
        if not self.stats:
            warn_item = TreeWidgetItem(self)
            warn_item.setData(
                0, Qt.DisplayRole,
                _('No timings to display. '
                  'Did you forget to add @profile decorators ?')
                .format(url=WEBSITE_URL))
            warn_item.setFirstColumnSpanned(True)
            warn_item.setTextAlignment(0, Qt.AlignCenter)
            font = warn_item.font(0)
            font.setStyle(QFont.StyleItalic)
            warn_item.setFont(0, font)
            return

        try:
            monospace_font = self.window().editor.get_plugin_font()
        except AttributeError:  # If run standalone for testing
            monospace_font = QFont("Courier New")
            monospace_font.setPointSize(10)

        for func_info, func_data in self.stats.items():
            # Function name and position
            filename, start_line_no, func_name = func_info
            func_stats, func_total_time = func_data
            func_item = TreeWidgetItem(self)
            func_item.setData(
                0, Qt.DisplayRole,
                _('{func_name} ({time_ms:.3f}ms) in file "{filename}", '
                  'line {line_no}').format(
                    filename=filename,
                    line_no=start_line_no,
                    func_name=func_name,
                    time_ms=func_total_time * 1e3))
            func_item.setFirstColumnSpanned(True)
            func_item.setData(COL_POS, Qt.UserRole,
                              (osp.normpath(filename), start_line_no))

            # For sorting by time
            func_item.setData(COL_TIME, Qt.DisplayRole, func_total_time * 1e3)
            func_item.setData(COL_PERCENT, Qt.DisplayRole,
                              func_total_time * 1e3)

            if self.parent().use_colors:
                # Choose deteministic unique color for the function
                md5 = hashlib.md5((filename + func_name).encode("utf8")).hexdigest()
                hue = (int(md5[:2], 16) - 68) % 360  # avoid blue (unreadable)
                func_color = QColor.fromHsv(hue, 200, 255)
            else:
                # Red color only
                func_color = QColor.fromRgb(255, 0, 0)

            # Lines of code
            for line_info in func_stats:
                line_item = TreeWidgetItem(func_item)
                (line_no, code_line, line_total_time, time_per_hit,
                 hits, percent) = line_info
                self.fill_item(
                    line_item, filename, line_no, code_line,
                    line_total_time, percent, time_per_hit, hits)

                # Color background
                if line_total_time is not None:
                    alpha = percent
                    color = QColor(func_color)
                    color.setAlphaF(alpha)  # Returns None
                    color = QBrush(color)
                    for col in range(self.columnCount()):
                        line_item.setBackground(col, color)
                else:

                    for col in range(self.columnCount()):
                        line_item.setForeground(col, CODE_NOT_RUN_COLOR)

                # Monospace font for code
                line_item.setFont(COL_LINE, monospace_font)
                
    def onItemClick(self, item):
        data = item.data(COL_POS, Qt.UserRole)
        if data is None or len(data)<2: return
        filename, line_no = data
        self.sig_edit_goto_requested.emit(filename, line_no, '')
