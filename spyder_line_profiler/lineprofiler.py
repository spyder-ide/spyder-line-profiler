# -*- coding:utf-8 -*-
#
# Copyright © 2013 Joseph Martinot-Lagarde
# based on p_profiler.py by Santiago Jaramillo
#
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Line profiler Plugin."""

# Third party imports
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QGroupBox, QLabel, QVBoxLayout

from spyder.config.main import CONF
from spyder.config.base import get_translation
from spyder.plugins import SpyderPluginMixin, PluginConfigPage, runconfig
from spyder.utils import icon_manager as ima
from spyder.utils.qthelpers import create_action

# Local imports
from .data import images
from .widgets.lineprofiler import LineProfilerWidget, is_lineprofiler_installed


_ = get_translation("line_profiler", dirname="spyder_line_profiler")


class LineProfilerConfigPage(PluginConfigPage):
    """
    Widget with configuration options for line profiler.
    """
    def setup_page(self):
        settings_group = QGroupBox(_("Settings"))
        use_color_box = self.create_checkbox(
            _("Use deterministic colors to differentiate functions"),
            'use_colors', default=True)

        results_group = QGroupBox(_("Results"))
        results_label1 = QLabel(_("Line profiler plugin results "
                                  "(the output of kernprof.py)\n"
                                  "are stored here:"))
        results_label1.setWordWrap(True)

        # Warning: do not try to regroup the following QLabel contents with
        # widgets above -- this string was isolated here in a single QLabel
        # on purpose: to fix Issue 863 of Profiler plugon
        results_label2 = QLabel(LineProfilerWidget.DATAPATH)

        results_label2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        results_label2.setWordWrap(True)

        settings_layout = QVBoxLayout()
        settings_layout.addWidget(use_color_box)
        settings_group.setLayout(settings_layout)

        results_layout = QVBoxLayout()
        results_layout.addWidget(results_label1)
        results_layout.addWidget(results_label2)
        results_group.setLayout(results_layout)

        vlayout = QVBoxLayout()
        vlayout.addWidget(settings_group)
        vlayout.addWidget(results_group)
        vlayout.addStretch(1)
        self.setLayout(vlayout)


class LineProfiler(LineProfilerWidget, SpyderPluginMixin):
    """
    Line profiler.
    """
    CONF_SECTION = 'lineprofiler'
    CONFIGWIDGET_CLASS = LineProfilerConfigPage
    edit_goto = Signal(str, int, str)

    def __init__(self, parent=None):
        LineProfilerWidget.__init__(self, parent=parent)
        SpyderPluginMixin.__init__(self, parent)

        # Initialize plugin
        self.initialize_plugin()

    # --- SpyderPluginWidget API ----------------------------------------------
    def get_plugin_title(self):
        """Return widget title."""
        return _("Line profiler")

    def get_plugin_icon(self):
        """Return widget icon."""
        path = images.__path__[0]
        return ima.icon('spyder.line_profiler', icon_path=path)

    def get_focus_widget(self):
        """
        Return the widget to give focus to when this plugin's dockwidget is
        raised on top-level.
        """
        return self.datatree

    def get_plugin_actions(self):
        """Return a list of actions related to plugin."""
        return []

    def on_first_registration(self):
        """Action to be performed on first plugin registration."""
        self.main.tabify_plugins(self.main.help, self)
        self.dockwidget.hide()

    def register_plugin(self):
        """Register plugin in Spyder's main window."""
        self.edit_goto.connect(self.main.editor.load)
        self.redirect_stdio.connect(self.main.redirect_internalshell_stdio)
        self.main.add_dockwidget(self)

        lineprofiler_act = create_action(self, _("Profile line by line"),
                                         icon=self.get_plugin_icon(),
                                         triggered=self.run_lineprofiler)
        lineprofiler_act.setEnabled(is_lineprofiler_installed())
        CONF.set(section="shortcuts",
                 option="Line Profiler/Run line profiler",
                 value="Shift+F10")
        self.register_shortcut(lineprofiler_act, context="Line Profiler",
                               name="Run line profiler", add_sc_to_tip=True)

        self.main.run_menu_actions += [lineprofiler_act]
        self.main.editor.pythonfile_dependent_actions += [lineprofiler_act]

    def refresh_plugin(self):
        """Refresh line profiler widget."""
        pass

    def closing_plugin(self, cancelable=False):
        """Perform actions before parent main window is closed."""
        return True

    def apply_plugin_settings(self, options):
        """Apply configuration file's plugin settings."""
        pass

    # --- Public API ----------------------------------------------------------
    def run_lineprofiler(self):
        """Run line profiler."""
        self.analyze(self.main.editor.get_current_filename())

    def analyze(self, filename):
        """Reimplement analyze method."""
        if self.dockwidget and not self.ismaximized:
            self.dockwidget.setVisible(True)
            self.dockwidget.setFocus()
            self.dockwidget.raise_()
        pythonpath = self.main.get_spyder_pythonpath()
        runconf = runconfig.get_run_configuration(filename)
        wdir, args = None, None
        if runconf is not None:
            if runconf.wdir_enabled:
                wdir = runconf.wdir
            if runconf.args_enabled:
                args = runconf.args

        LineProfilerWidget.analyze(
            self, filename, wdir=wdir, args=args, pythonpath=pythonpath,
            use_colors=self.get_option('use_colors', True))
