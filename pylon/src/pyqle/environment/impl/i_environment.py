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
A universe in which agents exist

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    Interface, Any, Instance, Int, Enum, Bool, Property, Float, List

#------------------------------------------------------------------------------
#  "IEnvironment" class:
#------------------------------------------------------------------------------

class IEnvironment(Interface):
    """
    A universe in which agents exist

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The state which the environment will be put into when initialised:
    initial_state = Instance("pylon.pyreto.environment.impl.istate.IState")

    # The current state of the environment:
    state = Instance("pylon.pyreto.environment.impl.istate.IState")

    # The list of action available in the current state:
    action_list = Property(List, depends_on=["state"]) # Instance(ActionList)

    # The reward for the last action applied:
    reward = Property(Float, depends_on=["state"])

    # True if the environment has reached the final state:
    is_final = Property(Bool(False), depends_on=["state"])

    # The winner of the game when the environment state is final:
    winner = Property(Any, depends_on=["is_final"])

    #--------------------------------------------------------------------------

    def _initial_state_default(self):
        """
        The enivronment's default initial state

        """


    def _get_action_list(self, event):
        """
        Gives the list of possible actions from a given state

        """


    def _get_reward(self):
        """
        Property getter

        """


    def _get_is_final(self):
        """
        Property getter

        """


    def _get_winner(self):
        """
        Property getter

        """

    #--------------------------------------------------------------------------

    def apply_action(self, action):
        """
        Computes the next state, given a start state and an action

        """

# EOF -------------------------------------------------------------------------
