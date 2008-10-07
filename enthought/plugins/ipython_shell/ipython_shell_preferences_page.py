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
#  Date:   14/06/2008
#
#------------------------------------------------------------------------------

"""
The preferences page for the IPython shell plug-in

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Bool, Enum, String

from enthought.traits.ui.api import \
    View, Group, HGroup, VGroup, Item, Label, Heading

from enthought.preferences.ui.api import PreferencesPage

#------------------------------------------------------------------------------
#  "IPythonShellPreferencesPage" class:
#------------------------------------------------------------------------------

class IPythonShellPreferencesPage(PreferencesPage):
    """ The preferences page for the IPython shell plug-in """

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
    name = "IPython Shell"

    # The path to the preferences node that contains the preferences.
    preferences_path = "enthought.plugins.ipython_shell"

    #--------------------------------------------------------------------------
    #  Preferences:
    #--------------------------------------------------------------------------

    # Choice of white or black background:
    background_colour = Enum("White", "Black")

    # Show the IPython banner with version numbers etc by default:
    ipython_banner = Bool(True, desc="Show the IPython banner on startup")

    # Message to display instead of the IPython banner:
    intro = String(desc="Banner to be shown instead of the IPython banner")

    # Enables Scintilla completion:
    completion_method = Enum(
        "IPython", "STC", desc="Optional Scintilla completion"
    )

    #--------------------------------------------------------------------------
    #  Traits UI views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Heading("IPython Shell"),
        Group(
            Item(name="ipython_banner", label="IPython"),
            Item(
                name="intro", label="Alternative",
                enabled_when="ipython_banner == False"
            ),
            Group(
                Label("Banner changes will not take effect until restart"),
            ),
            label="Banner",
            show_border=True
        ),
        Group(
            Item(name="background_colour"),
            Item(name="completion_method")
        )
    )

# EOF -------------------------------------------------------------------------
