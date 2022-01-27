# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2021, Spyder Line Profiler 5
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

# Local imports
from spyder_line_profiler.spyder.confpage import SpyderLineProfilerConfigPage
from spyder_line_profiler.spyder.widgets import SpyderLineProfilerWidget

_ = get_translation("spyder_line_profiler.spyder")


class SpyderLineProfiler(SpyderDockablePlugin):
    """
    Spyder Line Profiler plugin for Spyder 5.
    """

    NAME = "spyder_line_profiler"
    REQUIRES = [Plugins.Editor]
    OPTIONAL = []
    TABIFY = Plugins.Help
    WIDGET_CLASS = SpyderLineProfilerWidget
    CONF_SECTION = NAME
    CONF_WIDGET_CLASS = SpyderLineProfilerConfigPage

    # --- Signals

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
        widget = self.get_widget()

        # run_action = self.create_action(
        #     ProfilerActions.ProfileCurrentFile,
        #     text=_("Run profiler"),
        #     tip=_("Run profiler"),
        #     icon=self.create_icon('profiler'),
        #     triggered=self.run_profiler,
        #     register_shortcut=True,
        # )

        # run_action.setEnabled(is_profiler_installed())
        # editor = self.get_plugin(Plugins.Editor)
        # widget.sig_edit_goto_requested.connect(editor.load)
            
    def check_compatibility(self):
        valid = True
        message = ""  # Note: Remember to use _("") to localize the string
        return valid, message

    def on_close(self, cancellable=True):
        return True
        
    @on_plugin_available(plugin=Plugins.Editor)
    def on_editor_available(self):
        widget = self.get_widget()
        editor = self.get_plugin(Plugins.Editor)
        widget.editor = editor
        widget.sig_edit_goto_requested.connect(editor.load)
        
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
        self.widget.analyze(
            filename=filename,
            use_colors=self.get_option('use_colors', True))
