# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2021, Spyder Line Profiler contributors
#
# Licensed under the terms of the MIT license
# ----------------------------------------------------------------------------

"""
Spyder Line Profiler 5 Plugin.
"""

# Standard library imports
import os.path as osp

# Third-party imports
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QIcon
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.translations import get_translation
from spyder.api.plugin_registration.decorators import on_plugin_available
from spyder.api.plugin_registration.decorators import on_plugin_teardown
from spyder.plugins.mainmenu.api import ApplicationMenus
from spyder.utils.icon_manager import ima
import qtawesome as qta

# Local imports
from spyder_line_profiler.spyder.config import (
    CONF_SECTION, CONF_DEFAULTS, CONF_VERSION)
from spyder_line_profiler.spyder.confpage import SpyderLineProfilerConfigPage
from spyder_line_profiler.spyder.widgets import SpyderLineProfilerWidget
from spyder_line_profiler.spyder.widgets import is_lineprofiler_installed

# Localization
_ = get_translation("spyder_line_profiler.spyder")


class SpyderLineProfilerActions:
    # Triggers
    Run = 'run_profiler_action'


class SpyderLineProfiler(SpyderDockablePlugin):
    """
    Spyder Line Profiler plugin for Spyder 5.
    """

    NAME = "spyder_line_profiler"
    REQUIRES = [Plugins.Preferences, Plugins.Editor]
    OPTIONAL = [Plugins.MainMenu]
    TABIFY = [Plugins.Help]
    WIDGET_CLASS = SpyderLineProfilerWidget
    CONF_SECTION = CONF_SECTION
    CONF_DEFAULTS = CONF_DEFAULTS
    CONF_VERSION = CONF_VERSION
    CONF_WIDGET_CLASS = SpyderLineProfilerConfigPage
    CONF_FILE = True

    # --- Signals
    sig_finished = Signal()
    """This signal is emitted to inform the profile profiling has finished."""

    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------
    @staticmethod
    def get_name():
        return _("Line Profiler")

    def get_description(self):
        return _("Line profiler display for Spyder")

    def get_icon(self):
        return qta.icon('mdi.speedometer', color=ima.MAIN_FG_COLOR)

    def on_initialize(self):
        self.widget = self.get_widget()
        self.widget.sig_finished.connect(self.sig_finished)

        run_action = self.create_action(
            SpyderLineProfilerActions.Run,
            text=_("Run line profiler"),
            tip=_("Run line profiler"),
            icon=self.get_icon(),
            triggered=self.run_lineprofiler,
            context=Qt.ApplicationShortcut,
            register_shortcut=True,
        )
        run_action.setEnabled(is_lineprofiler_installed())

    @on_plugin_available(plugin=Plugins.MainMenu)
    def on_main_menu_available(self):
        mainmenu = self.get_plugin(Plugins.MainMenu)
        run_action = self.get_action(SpyderLineProfilerActions.Run)
        mainmenu.add_item_to_application_menu(
            run_action, menu_id=ApplicationMenus.Run)

    @on_plugin_teardown(plugin=Plugins.MainMenu)
    def on_main_menu_teardown(self):
        mainmenu = self.get_plugin(Plugins.MainMenu)
        mainmenu.remove_item_from_application_menu(
            SpyderLineProfilerActions.Run,
            menu_id=ApplicationMenus.Run
        )

    @on_plugin_available(plugin=Plugins.Preferences)
    def on_preferences_available(self):
        preferences = self.get_plugin(Plugins.Preferences)
        preferences.register_plugin_preferences(self)

    def check_compatibility(self):
        valid = True
        message = ""  # Note: Remember to use _("") to localize the string
        return valid, message

    def on_close(self, cancellable=True):
        return True

    # --- Public API
    # ------------------------------------------------------------------------
    def update_pythonpath(self):
        """
        Update the PYTHONPATH used when running the line_profiler.

        This function is called whenever the Python path set in Spyder changes.
        It synchronizes the PYTHONPATH in the line_profiler widget with the
        PYTHONPATH in Spyder.
        """
        self.widget.spyder_pythonpath = self.main.get_spyder_pythonpath()

    def run_lineprofiler(self):
        """Run line profiler."""
        editor = self.get_plugin(Plugins.Editor)
        if editor.save():
            self.switch_to_plugin()
            self.analyze(editor.get_current_filename())

        self.analyze(self.main.editor.get_current_filename())

    def analyze(self, filename):
        """Analyze a file."""
        if self.dockwidget:
            self.switch_to_plugin()
        self.widget.analyze(filename=filename)
