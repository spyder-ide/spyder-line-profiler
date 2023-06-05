# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
# Copyright (c) 2013- Spyder Project Contributors
#
# Released under the terms of the MIT License
# (see LICENSE.txt in the project root directory for details)
# -----------------------------------------------------------------------------

"""
Spyder Line Profiler Plugin.
"""

# Third-party imports
import qtawesome as qta
from qtpy.QtCore import Signal

# Spyder imports
import spyder
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.translations import get_translation
from spyder.api.plugin_registration.decorators import (
    on_plugin_available, on_plugin_teardown)
from spyder.plugins.mainmenu.api import ApplicationMenus, RunMenuSections
from spyder.utils.icon_manager import ima

if spyder.version_info[0] >= 6:
    from spyder.plugins.profiler.widgets.run_conf import (
        ProfilerPyConfigurationGroup)
    from spyder.plugins.run.api import RunContext, RunExecutor, run_execute
    USE_SPYDER6_RUN_PLUGIN = True
else:
    from qtpy.QtCore import Qt
    USE_SPYDER6_RUN_PLUGIN = False

# Local imports
from spyder_line_profiler.spyder.config import (
    CONF_SECTION, CONF_DEFAULTS, CONF_VERSION)
from spyder_line_profiler.spyder.confpage import SpyderLineProfilerConfigPage
from spyder_line_profiler.spyder.widgets import (
    SpyderLineProfilerWidget, is_lineprofiler_installed)

# Localization
_ = get_translation("spyder_line_profiler.spyder")


class SpyderLineProfilerActions:
    # Triggers
    Run = 'Run file in spyder_line_profiler'


if USE_SPYDER6_RUN_PLUGIN:
    PLUGIN_BASE_CLASSES = [SpyderDockablePlugin, RunExecutor]
else:
    PLUGIN_BASE_CLASSES = [SpyderDockablePlugin]


class SpyderLineProfiler(*PLUGIN_BASE_CLASSES):
    """
    Spyder Line Profiler plugin for Spyder 5.
    """

    NAME = "spyder_line_profiler"

    if USE_SPYDER6_RUN_PLUGIN:
        REQUIRES = [Plugins.Preferences, Plugins.Editor, Plugins.Run]
        OPTIONAL = []
    else:
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

        if USE_SPYDER6_RUN_PLUGIN:
            self.executor_configuration = [
                {
                    'input_extension': 'py',
                    'context': {
                        'name': 'File'
                    },
                    'output_formats': [],
                    'configuration_widget': ProfilerPyConfigurationGroup,
                    'requires_cwd': True,
                    'priority': 7
                }
            ]
        else:
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

    if USE_SPYDER6_RUN_PLUGIN:
        @on_plugin_available(plugin=Plugins.Run)
        def on_run_available(self):
            run = self.get_plugin(Plugins.Run)
            run.register_executor_configuration(self, self.executor_configuration)

            if is_lineprofiler_installed():
                run.create_run_in_executor_button(
                    RunContext.File,
                    self.NAME,
                    text=_('Run line profiler'),
                    tip=_('Run line profiler'),
                    icon=self.get_icon(),
                    shortcut_context='spyder_line_profiler',
                    register_shortcut=True,
                    add_to_menu={
                        "menu": ApplicationMenus.Run,
                        "section": RunMenuSections.RunInExecutors
                    }
                )

        @on_plugin_teardown(plugin=Plugins.Run)
        def on_run_teardown(self):
            run = self.get_plugin(Plugins.Run)
            run.deregister_executor_configuration(
                self, self.executor_configuration)
            run.destroy_run_in_executor_button(
                RunContext.File, self.NAME)

    else:
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

    @on_plugin_teardown(plugin=Plugins.Preferences)
    def on_preferences_teardown(self):
        preferences = self.get_plugin(Plugins.Preferences)
        preferences.deregister_plugin_preferences(self)

    def check_compatibility(self):
        valid = True
        message = ""  # Note: Remember to use _("") to localize the string
        return valid, message

    def on_close(self, cancellable=True):
        return True

    # --- Public API
    # ------------------------------------------------------------------------

    if USE_SPYDER6_RUN_PLUGIN:
        @run_execute(context=RunContext.File)
        def run_file(self, input, conf):
            self.switch_to_plugin()

            exec_params = conf['params']
            cwd_opts = exec_params['working_dir']
            params = exec_params['executor_params']

            run_input = input['run_input']
            filename = run_input['path']

            wdir = cwd_opts['path']
            args = params['args']

            self.get_widget().analyze(filename, wdir=wdir, args=args)

    else:
        def run_lineprofiler(self):
            """Run line profiler."""
            editor = self.get_plugin(Plugins.Editor)
            if editor.save():
                self.switch_to_plugin()
                self.analyze(editor.get_current_filename())

        def analyze(self, filename):
            """Analyze a file."""
            if self.dockwidget:
                self.switch_to_plugin()
            self.widget.analyze(filename=filename)
