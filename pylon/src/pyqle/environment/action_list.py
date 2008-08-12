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
A place to put actions : used when looking for the list of possible moves

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import \
    HasTraits, Instance, Int, Bool, List, Property

# Pyqle imports:
from pyqle.environment.i_action import IAction

from pyqle.environment.state import State

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ActionList" class:
#------------------------------------------------------------------------------

class ActionList(HasTraits):
    """
    A place to put actions : used when looking for the list of possible moves

    """

    actions = List(IAction)

    n_actions = Property(Int, depends_on=["actions, actions_items"])

    state = Instance(State)


    def __init__(self, state, **traits):
        self.state = state

        super(ActionList, self).__init__(state=state, **traits)


    def add(self, action):
        """
        Adds an action

        """

        if action not in self.actions:
            self.actions.append(action)
        return True


    def _get_n_actions(self):
        """
        Property getter

        """

        return len(self.actions)


    def get_action(self, i):
        """
        Get Action at rank i

        """

        if (len(self.actions) != 0):
            return self.actions[i]
        else:
            return


    def to_string(self):
        s = ""
        for i in self.n_actions:
            s += "\n Action Agent " + i + ":" + self.get_action(i)
        return s

# EOF -------------------------------------------------------------------------
