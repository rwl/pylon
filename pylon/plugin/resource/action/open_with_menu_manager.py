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
#  Date:   24/07/2008
#
#------------------------------------------------------------------------------

""" The "Open With" menu """

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

EDITORS = "enthought.plugins.workspace.editors"

#------------------------------------------------------------------------------
#  "OpenWithMenuManager" class:
#------------------------------------------------------------------------------

class OpenWithMenuManager(MenuManager):
    """ The "Open With" menu """

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
