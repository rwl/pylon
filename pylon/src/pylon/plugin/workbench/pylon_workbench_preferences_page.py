#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

""" Pylon workbench plug-in with customised actions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.ui.api import View, Item, Group, Label, Heading

from enthought.envisage.ui.workbench.workbench_preferences_page import \
    WorkbenchPreferencesPage

#------------------------------------------------------------------------------
#  "PylonWorkbenchPreferencesPage" class:
#------------------------------------------------------------------------------

class PylonWorkbenchPreferencesPage(WorkbenchPreferencesPage):
    """ Extended with a heading """

    # Traits UI views ---------------------------------------------------------

    trait_view = View(
        Heading("Workbench"),
        "_",
        Group(
              Item(name="prompt_on_exit"),
        )
    )

# EOF -------------------------------------------------------------------------
