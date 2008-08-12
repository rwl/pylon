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

""" Defines the selector interface """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Interface, Str

#------------------------------------------------------------------------------
#  "ISelector" class:
#------------------------------------------------------------------------------

class ISelector(Interface):
    """ Defines the selector interface """

    # Human readable identifier
    name = Str("Selector")


    def choose(self, state, action_list):
        """ Choose an action from a list of actions

        @param state The state the for which the actions apply
        @param action_list The list of possible actions from which to choose

        """

        pass


    def learn(self, starting_state, action, resulting_state, reward):
        """ Learn from the starting state, the chosen action, the resulting
        state and the reward given by the environment

        Learn
         @param starting_state The state the agent is in before the action
         is performed.
         @param action The action the agent took.
         @param resulting_state The state the agent goes to when the action
         is performed.
         @param reward The reward obtained for this move.

        """

        pass

# EOF -------------------------------------------------------------------------
