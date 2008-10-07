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

""" An Agent that is part of a swarm. It has a local environment that
provides a list of actions from which it selects when the swarm calls
the choose method.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import \
    HasTraits, Any, Instance, Int, Enum, Bool, Float, Delegate

from pyqle.environment.elementary_environment import ElementaryEnvironment

from pyqle.environment.state_filter import StateFilter

from agent import Agent

#------------------------------------------------------------------------------
#  Setup a logger for this module:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ElementaryAgent" class:
#------------------------------------------------------------------------------

class ElementaryAgent(Agent):
    """ An Agent that is part of a swarm. It has a local environment that
    provides a list of actions from which it selects when the swarm calls
    the choose method.

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Override to ensure ElementaryEnvironment is used
    environment = Instance(ElementaryEnvironment, allow_none=False)

    # Container of all elementary agents:
#    swarm = Instance("pyqle.agent.swarm.Swarm", allow_none=False)

    # State is delegated from swarm which is in turn delegated from environment
#    state = Delegate("swarm")

    # Method class that return the state of the environment as perceived by
    # the ElementaryAgent:
#    state_filter = Instance(StateFilter, allow_none=False)

    # Each elementary agent adds some part of reward to the global reward
    #
    # In some cases (to be defined), environment may deliver individual rewards to
    # elementary agents
#    internal_reward = Float

    # A number identifying an ElementaryAgent inside a swarm
#    rank = Int(0)


#    def _state_changed_for_environment(self, env, name, old_state, new_state):
#        """
#        Override environment state change event handler
#
#        """
#
#        filtered_state = self.state_filter.filter_state(
#            self.state,
#            self.environment
#        )
#
#        chosen_action = self._choose(filtered_state, env.action_list)
#
#        self._apply_action(chosen_action)


    def choose(self, state, action_list):
        """ Ask the algorithm to choose the next action

        Overridden here so as to get the list of actions from the local env.

        """

        logger.debug(
            "Elementary agent [%s] getting an action list from its local "
            "environment [%s]" % (self.name, self.environment.name)
        )

        action_list = self.environment.action_list

        logger.debug(
            "Elementary agent [%s] asking the selector [%s] to choose the "
            "next action" % (self.name, self.selector)
        )

        choice = self.selector.choose(state, action_list)

        logger.debug(
            "Elementary agent [%s] selected an action [%s]" %
            (self.name, choice)
        )

        return choice


    def _apply_action(self, action):
        """ Add the action to the composed action of the swarm """

        pass


#    def set_current_state(self, state):
#        self.old_state = self.current_state.copy()
#        self.current_state = self.filter.filter_state(state,
#            self.universe)


#    def set_initial_state(self, state):
#        """
#        Place the agent
#
#        """
#
#        self.current_state = self.filter.filter_state(state,
#            self.universe)
#        self.old_state = self.current_state.copy()

# EOF -------------------------------------------------------------------------
