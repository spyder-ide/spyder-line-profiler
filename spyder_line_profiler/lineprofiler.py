# -*- coding: utf-8 -*-
#
# Copyright © 2013 Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""Line profiler Plugin."""

# Third party imports
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QGroupBox, QLabel, QVBoxLayout

# Need running QApplication before importing runconfig
from spyder.utils.qthelpers import qapplication
MAIN_APP = qapplication()

from spyder.api.plugins import SpyderPluginWidget
from spyder.api.preferences import PluginConfigPage
from spyder.config.base import get_translation
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


class LineProfiler(SpyderPluginWidget):
    """
    Line profiler.
    """
    CONF_SECTION = 'lineprofiler'
    CONFIGWIDGET_CLASS = LineProfilerConfigPage
    edit_goto = Signal(str, int, str)

    def __init__(self, parent=None):
        SpyderPluginWidget.__init__(self, parent)

        # Create widget and add to dockwindow
        self.widget = LineProfilerWidget(self.main)
        layout = QVBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def update_pythonpath(self):
        """
        Update the PYTHONPATH used when running the line_profiler.

        This function is called whenever the Python path set in Spyder changes.
        It synchronizes the PYTHONPATH in the line_profiler widget with the
        PYTHONPATH in Spyder.
        """
        self.widget.spyder_pythonpath = self.main.get_spyder_pythonpath()

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
        return self.widget.datatree

    def get_plugin_actions(self):
        """Return a list of actions related to plugin."""
        return []

    def on_first_registration(self):
        """Action to be performed on first plugin registration."""
        self.main.tabify_plugins(self.main.help, self)
        self.dockwidget.hide()

    def register_plugin(self):
        """Register plugin in Spyder's main window."""
        super(LineProfiler, self).register_plugin()

        # Spyder PYTHONPATH
        self.update_pythonpath()
        self.main.sig_pythonpath_changed.connect(self.update_pythonpath)

        self.edit_goto.connect(self.main.editor.load)
        self.widget.redirect_stdio.connect(self.main.redirect_internalshell_stdio)

        lineprofiler_act = create_action(self, _("Profile line by line"),
                                         icon=self.get_plugin_icon(),
                                         shortcut="Shift+F10",
                                         triggered=self.run_lineprofiler)
        lineprofiler_act.setEnabled(is_lineprofiler_installed())

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
        if self.dockwidget:
            self.switch_to_plugin()
        self.widget.analyze(
            filename=filename,
            use_colors=self.get_option('use_colors', True))
