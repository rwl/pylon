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

""" Customised "View" ("Window") menu """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Str, Unicode
from enthought.pyface.action.api import Group, MenuManager
from enthought.pyface.workbench.action.api import ViewMenuManager
from enthought.pyface.workbench.action.perspective_menu_manager import \
    PerspectiveMenuManager

from pylon_workbench_action import \
    NewWindowAction, NewEditorAction, PreferencesAction

#------------------------------------------------------------------------------
#  "PylonViewMenuManager" class:
#------------------------------------------------------------------------------

class PylonViewMenuManager(ViewMenuManager):
    """ Customised "View" ("Window") menu """

    #--------------------------------------------------------------------------
    #  "ActionManager" interface:
    #--------------------------------------------------------------------------

    # The manager's unique identifier (if it has one).
    id = Str("Window")

    #--------------------------------------------------------------------------
    #  "MenuManager" interface:
    #--------------------------------------------------------------------------

    # The menu manager's name (if the manager is a sub-menu, this is what its
    # label will be).
    name = Unicode("&Window")

    #--------------------------------------------------------------------------
    #  "ActionManager" interface:
    #--------------------------------------------------------------------------

    def _groups_default(self):
        """ Trait initialiser """

#        groups = super(PylonViewMenuManager, self)._groups_default()

        groups = []

        new_group = Group(id="NewGroup")
        new_group.append(NewWindowAction(window=self.window))
        # FIXME: Changing the enabled trait of the NewEditorAction causes barf
#        new_group.append(NewEditorAction(window=self.window))
        # Insert a group for new part actions
        groups.append(new_group)

        # Add a group for view and perspective sub menus
        submenu_group = Group(id="SubMenuGroup")
        # Add the perspective menu (if requested).
        if self.show_perspective_menu and len(self.window.perspectives) > 0:
            submenu_group.append(PerspectiveMenuManager(window=self.window))
        # TODO: Create a ViewMenuManager with a selection of views
        view_submenu = MenuManager(
            self._create_other_group(self.window), name="Show View"
        )
        submenu_group.append(view_submenu)
        groups.append(submenu_group)

        # Add a group containing a 'toggler' for all visible views.
        self._view_group = self._create_view_group(self.window)
        groups.append(self._view_group)

        # Add a group containing the preferences action
        groups.append(Group(PreferencesAction(window=self.window)))

        return groups

# EOF -------------------------------------------------------------------------
