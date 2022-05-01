# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2021, Spyder Line Profiler contributors
#
# Licensed under the terms of the MIT license
# ----------------------------------------------------------------------------

"""
Spyder Line Profiler 5 Preferences Page.
"""

# Third party imports
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, QVBoxLayout
from spyder.api.preferences import PluginConfigPage
from spyder.api.translations import get_translation

# Local imports
from .widgets import SpyderLineProfilerWidget

# Localization
_ = get_translation("spyder_line_profiler.spyder")


class SpyderLineProfilerConfigPage(PluginConfigPage):

    # --- PluginConfigPage API
    # ------------------------------------------------------------------------

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
        # on purpose: to fix Issue 863 of Profiler plugin
        results_label2 = QLabel(SpyderLineProfilerWidget.DATAPATH)

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