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

""" Defines the preferences page for the resource plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import expanduser, join

from enthought.traits.api import Bool, Enum, String, Directory

from enthought.traits.ui.api import \
    View, Group, HGroup, VGroup, Item, Label, Heading

from enthought.preferences.ui.api import PreferencesPage

#------------------------------------------------------------------------------
#  "ResourcePreferencesPage" class:
#------------------------------------------------------------------------------

class ResourcePreferencesPage(PreferencesPage):
    """ Defines the preferences page for the resource plug-in """

    #--------------------------------------------------------------------------
    #  "PreferencesPage" interface:
    #--------------------------------------------------------------------------

    # The page's category (e.g. 'General/Appearance'). The empty string means
    # that this is a top-level page.
    category = "General"

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ""

    # The page name (this is what is shown in the preferences dialog.
    name = "Resource"

    # The path to the preferences node that contains the preferences.
    preferences_path = "pylon.plugin.resource"

    #--------------------------------------------------------------------------
    #  Preferences:
    #--------------------------------------------------------------------------

    # Prompt for workspace on startup?
#    prompt = Bool(True)

    # The default workspace to use without prompting
    default = Directory(expanduser("~"), exists=False,
        desc="the default workspace directory location"
    )

    # Refresh workspace on startup?
#    refresh = Bool(False)

    #--------------------------------------------------------------------------
    #  Traits UI views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Heading("Resource"),
#        Group(
#            Item(name="prompt", label="Prompt for workspace on startup."),
#            show_left=False
#        ),
#        Item(name="default", enabled_when="prompt==False", show_label=False),
#        Group(
#            Item(name="refresh", label="Refresh workspace on startup.", enabled_when="False"),
#            show_left=False
#        )
    )

# EOF -------------------------------------------------------------------------
