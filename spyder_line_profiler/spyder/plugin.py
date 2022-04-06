# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2021, Spyder Line Profiler contributors
#
# Licensed under the terms of the MIT license
# ----------------------------------------------------------------------------
"""
Spyder Line Profiler 5 Plugin.
"""

# Third-party imports
from qtpy.QtGui import QIcon

# Spyder imports
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.translations import get_translation
from spyder.api.plugin_registration.decorators import on_plugin_available
from spyder.api.plugin_registration.decorators import on_plugin_teardown
from qtpy.QtCore import Signal

# Local imports
from spyder.plugins.mainmenu.api import ApplicationMenus
from spyder_line_profiler.spyder.confpage import SpyderLineProfilerConfigPage
from spyder_line_profiler.spyder.widgets import SpyderLineProfilerWidget
from spyder_line_profiler.spyder.widgets import SpyderLineProfilerWidgetActions
from spyder_line_profiler.spyder.widgets import is_lineprofiler_installed

_ = get_translation("spyder_line_profiler.spyder")



class SpyderLineProfilerActions:
    # Triggers
    Run = 'run_action_menu'
    

class SpyderLineProfiler(SpyderDockablePlugin):
    """
    Spyder Line Profiler plugin for Spyder 5.
    """

    NAME = "spyder_line_profiler"
    REQUIRES = [Plugins.Editor, Plugins.Help]
    OPTIONAL = [Plugins.MainMenu]
    TABIFY = [Plugins.Help]
    WIDGET_CLASS = SpyderLineProfilerWidget
    CONF_SECTION = NAME
    CONF_WIDGET_CLASS = SpyderLineProfilerConfigPage

    # --- Signals
    sig_finished = Signal()
    """This signal is emitted to inform the profile profiling has finished."""

    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------
    @staticmethod
    def get_name():
        return _("Line Profiler")

    def get_description(self):
        return _("Line profiler display for Spyder 5")

    def get_icon(self):
        return QIcon('./data/images/spyder.line_profiler.png')

    def on_initialize(self):
        self.widget = self.get_widget()
        self.widget.sig_finished.connect(self.sig_finished)
        
        run_action = self.create_action(
                        SpyderLineProfilerActions.Run,
                        text=_("Run line profiler"),
                        tip=_("Run line profiler"),
                        icon=self.get_icon(),
                        triggered=self.run_lineprofiler,
                        register_shortcut=True,
                        )   
        run_action.setEnabled(is_lineprofiler_installed())
        
        
    @on_plugin_available(plugin=Plugins.MainMenu)
    def on_main_menu_available(self):
        mainmenu = self.get_plugin(Plugins.MainMenu)
        start_action = self.get_action(SpyderLineProfilerActions.Run)
        mainmenu.add_item_to_application_menu(
            start_action, menu_id=ApplicationMenus.Run)
        
    @on_plugin_teardown(plugin=Plugins.MainMenu)
    def on_main_menu_teardown(self):
        mainmenu = self.get_plugin(Plugins.MainMenu)

        mainmenu.remove_item_from_application_menu(
            SpyderLineProfilerActions.ProfileCurrentFile,
            menu_id=ApplicationMenus.Run
        )    
        
        
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
        """Reimplement analyze method."""        
        if self.dockwidget:
            self.switch_to_plugin()
        self.widget.analyze(filename=filename)
