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
A place to put actions: used when looking for the list of possible moves

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Interface, Instance, Int, List, Property

#------------------------------------------------------------------------------
#  "IActionList" class:
#------------------------------------------------------------------------------

class IActionList(HasTraits):
    """
    A place to put actions: used when looking for the list of possible moves

    """

    actions = List(Instance("pylon.pyreto.environment.impl.iaction.IAction"))

    n_actions = Property(Int, depends_on=["actions, actions_items"])

    state = Instance(
        "pylon.pyreto.environment.impl.istate.IState",
        allow_none=False
    )


    def add(self, action):
        """
        Adds an action

        """


    def _get_n_actions(self):
        """
        Property getter

        """


    def get_action(self, i):
        """
        Get Action at rank i

        """


    def to_string(self):
        """
        String representation of the object

        """

# EOF -------------------------------------------------------------------------
