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

""" The 'Open With' menu """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.pyface.action.api import Group, MenuManager
from enthought.traits.api import Any, Bool, Instance, List, Str, Unicode
from enthought.traits.api import on_trait_change
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow
from enthought.plugins.workspace.action.open_with_action import OpenWithAction

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

EDITORS = "pylon.plugin.resource.editors"

#------------------------------------------------------------------------------
#  "OpenWithMenuManager" class:
#------------------------------------------------------------------------------

class OpenWithMenuManager(MenuManager):
    """ The 'Open With' menu """

    #--------------------------------------------------------------------------
    #  "ActionManager" interface
    #--------------------------------------------------------------------------

    # All of the groups in the manager.
    groups = List(Group)

    # The manager"s unique identifier (if it has one).
    id = Str("OpenWith")

    #--------------------------------------------------------------------------
    #  "MenuManager" interface
    #--------------------------------------------------------------------------

    # The menu manager"s name (if the manager is a sub-menu, this is what its
    # label will be).
    name = Unicode("Open With")

    #--------------------------------------------------------------------------
    #  "OpenWithMenuManager" interface
    #--------------------------------------------------------------------------

    # The workbench window that the menu is part of.
    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "ActionManager" interface
    #--------------------------------------------------------------------------

    def _groups_default(self):
        """ Trait initialiser """

        app = self.window.application
        editors = [factory() for factory in app.get_extensions(EDITORS)]

        editors_group = Group(id="editors")

        for editor in editors:
            action = OpenWithAction(
                editor=editor, window=self.window
            )
            editors_group.append(action)

        return [editors_group]

# EOF -------------------------------------------------------------------------
