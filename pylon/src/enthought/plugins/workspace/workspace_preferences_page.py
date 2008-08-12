#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Richard W. Lincoln
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Richard W. Lincoln
#  Date:   10/07/2008
#
#------------------------------------------------------------------------------

""" Defines the preferences page for the Workspace plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import expanduser, join

from enthought.traits.api import Bool, Enum, String, Directory

from enthought.traits.ui.api import \
    View, Group, HGroup, VGroup, Item, Label, Heading

from enthought.preferences.ui.api import PreferencesPage

#------------------------------------------------------------------------------
#  "WorkspacePreferencesPage" class:
#------------------------------------------------------------------------------

class WorkspacePreferencesPage(PreferencesPage):
    """ Defines the preferences page for the Workspace plug-in """

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
    name = "Workspace"

    # The path to the preferences node that contains the preferences.
    preferences_path = "enthought.plugins.workspace"

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
        Heading("Workspace"),
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
