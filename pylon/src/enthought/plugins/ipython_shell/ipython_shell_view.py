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
IPython shell view

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.envisage.api import IExtensionRegistry

from enthought.envisage.api import ExtensionPoint

from enthought.pyface.workbench.api import View as WorkbenchView

from enthought.traits.api import Instance, Property

from enthought.pyface.ipython_shell import IPythonShell

from enthought.preferences.api import bind_preference

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "IPythonShellView" class:
#------------------------------------------------------------------------------

class IPythonShellView(WorkbenchView):
    """ IPython shell view """

    #--------------------------------------------------------------------------
    #  "IView" interface:
    #--------------------------------------------------------------------------

    # The view"s globally unique identifier:
    id = "enthought.plugins.ipython_shell_view"

    # The view"s name:
    name = "IPython Shell"

    # The default position of the view relative to the item specified in the
    # "relative_to" trait.
    position = "bottom"

    #--------------------------------------------------------------------------
    #  "IExtensionPointUser" interface:
    #--------------------------------------------------------------------------

    # The extension registry that the object's extension points are stored in.
    extension_registry = Property(Instance(IExtensionRegistry))

    #--------------------------------------------------------------------------
    #  Private interface:
    #--------------------------------------------------------------------------

    # Bindings.
    _bindings = ExtensionPoint(id="enthought.plugins.ipython_shell.bindings")

    # Commands.
    _commands = ExtensionPoint(id="enthought.plugins.ipython_shell.commands")

    #--------------------------------------------------------------------------
    #  "IExtensionPointUser" interface:
    #--------------------------------------------------------------------------

    def _get_extension_registry(self):
        """ Trait property getter. """

        return self.window.application

    #--------------------------------------------------------------------------
    #  "IView" interface:
    #--------------------------------------------------------------------------

    def create_control(self, parent):
        """
        Create the view contents

        """

        colour = self.window.application.preferences.get(
            "enthought.plugins.ipython_shell.background_colour", "White"
        )

        banner = self.window.application.preferences.get(
            "enthought.plugins.ipython_shell.ipython_banner", "True"
        )

        # FIXME: Implement PreferencesHelper for type coercion
        if banner == "False":
            banner = False
        else:
            banner = True

        intro = self.window.application.preferences.get(
            "enthought.plugins.ipython_shell.intro", ""
        )

        completion = self.window.application.preferences.get(
            "enthought.plugins.ipython_shell.completion_method", "IPython"
        )

        # Instantiate the widget
        shell = IPythonShell(
            parent, background_colour=colour, ipython_banner=banner,
            intro=intro, completion_method=completion
        )

        # Bind namespace contributions
        for bindings in self._bindings:
            for name, value in bindings.items():
                shell.control.IP.updateNamespace({name: value})

        # Execute contributed commands
        for command in self._commands:
            shell.control.IP.doExecute(command)

        # Bind the shell"s traits to preferences
        bind_preference(
            shell, "background_colour",
            "enthought.plugins.ipython_shell.background_colour"
        )

        bind_preference(
            shell, "ipython_banner",
            "enthought.plugins.ipython_shell.ipython_banner"
        )

        bind_preference(
            shell, "intro",
            "enthought.plugins.ipython_shell.intro"
        )

        bind_preference(
            shell, "completion_method",
            "enthought.plugins.ipython_shell.completion_method"
        )

        return shell.control

# EOF -------------------------------------------------------------------------
