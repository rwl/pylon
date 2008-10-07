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
IPython shell plugin

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.envisage.api import Plugin, ExtensionPoint

from enthought.traits.api import List, Dict, String

from enthought.pyface.ui.wx.ipython_shell import IPythonShell

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "IPythonShellPlugin" class:
#------------------------------------------------------------------------------

class IPythonShellPlugin(Plugin):
    """ IPython shell plugin """

    # Extension point IDs
    BINDINGS = "enthought.plugins.ipython_shell.bindings"
    COMMANDS = "enthought.plugins.ipython_shell.commands"
    VIEWS = "enthought.envisage.ui.workbench.views"
    PREFERENCES_PAGES = "enthought.envisage.ui.workbench.preferences_pages"

    # Unique plugin identifier
    id = "enthought.plugins.ipython_shell"

    # Human readable plugin name
    name = "IPython Shell"

    #--------------------------------------------------------------------------
    #  Extensions points:
    #--------------------------------------------------------------------------

    bindings = ExtensionPoint(
        List(Dict), id=BINDINGS, desc="""

        This extension point allows you to contribute name/value pairs that
        will be bound when the interactive IPython shell is started.

        e.g. Each item in the list is a dictionary of name/value pairs::

        {"x" : 10, "y" : ["a", "b", "c"]}

        """
    )

    commands = ExtensionPoint(
        List(String), id=COMMANDS, desc="""

        This extension point allows you to contribute commands that are
        executed when the interactive IPython shell is started.

        e.g. Each item in the list is a string of arbitrary Python code::

          "import os, sys"
          "from enthought.traits.api import *"

        Yes, I know this is insecure but it follows the usual Python rule of
        "we are all consenting adults".

        """
    )

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Bindings:
    contributed_bindings = List(contributes_to=BINDINGS)

    # Contributed views:
    contributed_views = List(contributes_to=VIEWS)

    # Contributed preference pages:
    preferences_pages = List(contributes_to=PREFERENCES_PAGES)

    #--------------------------------------------------------------------------
    #  "IPythonShellPlugin" interface:
    #--------------------------------------------------------------------------

    def _contributed_bindings_default(self):
        """ Trait initialiser. """

        return [{"application" : self.application}]


    def _contributed_views_default(self):
        """ Trait initialiser """

        from ipython_shell_view import IPythonShellView

        return [IPythonShellView]


    def _preferences_pages_default(self):
        """ Trait initialiser """

        from ipython_shell_preferences_page import IPythonShellPreferencesPage

        return [IPythonShellPreferencesPage]

# EOF -------------------------------------------------------------------------
