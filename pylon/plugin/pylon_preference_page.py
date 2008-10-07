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

"""
The preference pages for Pylon

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join

from enthought.etsconfig.api import ETSConfig

from enthought.traits.api import Float, File, Bool

from enthought.traits.ui.api import View, Group, HGroup, VGroup, Item, Label

from enthought.preferences.ui.api import PreferencesPage

#------------------------------------------------------------------------------
#  "PylonRootPreferencesPage" class:
#------------------------------------------------------------------------------

class PylonRootPreferencePage(PreferencesPage):
    """ Root preferences page for Pylon """

    #--------------------------------------------------------------------------
    #  "PreferencesPage" interface:
    #--------------------------------------------------------------------------

    # The page's category (e.g. 'General/Appearance'). The empty string means
    # that this is a top-level page.
    category = ""

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ""

    # The page name (this is what is shown in the preferences dialog.
    name = "Pylon"

    # The path to the preferences node that contains the preferences.
    preferences_path = "pylon"

    #--------------------------------------------------------------------------
    #  Preferences:
    #--------------------------------------------------------------------------

#    persist_project = Bool(True, desc="persisting of project between sessions")
#
#    persistence_path = File(
#        ETSConfig.application_home,
#        desc="the directory to which the pylon project should be pickled"
#    )

    #--------------------------------------------------------------------------
    #  Traits UI views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Label("Pylon"),
        "_",
#        Group(
#            Item(name="persist_project", label="Persist"),
#            Item(
#                name="persistence_path",
#                enabled_when="persist_project",
#                label="Path"
#            )
#        )
    )

# EOF -------------------------------------------------------------------------
