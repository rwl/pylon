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

""" A base class for many agents """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import \
    HasTraits, Instance, Int, Enum, Bool, Delegate, List, Property, \
    String, Float, on_trait_change, Array

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, VGroup, Tabbed

from enthought.chaco.chaco_plot_editor import ChacoPlotItem

from pyqle.environment.environment import Environment
from pyqle.selector.i_selector import ISelector
from pyqle.selector.random_selector import RandomSelector
from pyqle.selector.human_selector import HumanSelector
from pyqle.selector.profile_selector import ProfileSelector
from pyqle.environment.state import State
from pyqle.environment.i_action import IAction

#------------------------------------------------------------------------------
#  Setup a logger for this module:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Agent" class:
#------------------------------------------------------------------------------

class Agent(HasTraits):
    """ A base class for many agents """

    # Human readable identifier:
    name = String("Untitled")

    # The universe with which the agent interacts:
    environment = Instance(Environment, allow_none=False)

    # A selection of selectors:
    selectors = List(
        Instance(ISelector), desc="list of selectors from which to choose"
    )

    # The algorithm which selects an action from a list of possible ones:
    selector = Instance(ISelector)

    # The current state of the agent:
    state = Delegate("environment")

    # The previous state of the agent:
    old_state = Instance(State)

    # The last action performed by this agent:
    last_action = Instance(IAction)

    # Control if the agent is to learn when a new reward is received:
    learning_enabled = Bool(True)

    # Last reward received:
    reward = Float(transient=True)

    # All received rewards:
    rewards = List(Float, transient=True)
    _periods = Property(Array, depends_on=["reward"])
    _rewards = Property(Array, depends_on=["reward"]) # For plotting

    traits_view = View(
        VGroup(
            HGroup(
                Item(
                    name="selector", show_label=False,
                    editor=InstanceEditor(name="selectors", editable=False)
                ),
                Item(name="selector", style="simple", show_label=False),
            ),
            Group(
                Item(name="reward", style="readonly", label="Last reward"),
                Group(
                    ChacoPlotItem(
                        "_periods", "_rewards",
                        type="line",
                        # Basic axis and label properties
                        show_label=False, resizable=True, orientation="h",
                        title="Rewards", x_label="period", y_label="Reward",
                        # Plot properties
                        color="turquoise", bgcolor="ivory",
                        # Border properties
                        border_color="darkblue", #border_width=2,
                        # Specific to scatter plot
                        marker="circle", marker_size=4, outline_color="green",
                        # Border, padding properties
                        border_visible=True, border_width=1,
                        padding_bg_color="lightblue"
                    ),
                ),
                label="Rewards", show_border=True
            ),
            Group(
                  Item(name="environment", style="custom", show_label=False),
                  label="Environment", show_border=True
            )
        ),
        id="agent_view.default_view", resizable=True,
    )

    #--------------------------------------------------------------------------
    #  Protected interface
    #--------------------------------------------------------------------------

    def _selectors_default(self):
        """ Trait initialiser """

        return [RandomSelector(), HumanSelector(), ProfileSelector()]


    def _selector_default(self):
        """ Trait initialiser """

        if self.selectors:
            return self.selectors[0]
        else:
            return None


    def _state_changed_for_environment(self, env, name, old_state, new_state):
#    def _state_changed(self, old_state, new_state):
        """ Handle environment state changing """

        chosen_action = self._choose(new_state, env.action_list)

        self._apply_action(chosen_action)


    def choose(self, state, action_list):
        """ Ask the algorithm to choose the next action """

        if self.selector is not None:
            choice = self.selector.choose(action_list)
        else:
            if action_list:
                choice = action_list[0]
            else:
                choice = None

        return choice


    def _apply_action(self, action):
        """ Apply the action and wait for the reward """

#        self.old_state = self.current_state
#        self.current_state = self.universe.successor_state(self.current_state,
#                                                           action)
#        return action

        self.old_state = self.state.copy()
        self.environment.apply_action(action)
        self.last_action = action.copy()


    @on_trait_change("reward")
    def _reward_changed_for_environment(self, new):
        """ Listen for any reward forthcoming. If learning is enabled,
        learn from states, action, and reward

        """

        logger.debug("Agent [%s] received reward [%s]" % (self.name, new))

        # Maintain a record of reward received
        self.rewards.append(new)

        if self.learning_enabled:
            self.selector.learn(
                self.old_state, self.state, self.last_action, new
            )


    def _get__periods(self):
        """ Property getter """

        if self.rewards:
            return [i for i in range(1, len(self.rewards)+1)]
        else:
            return [0]


    def _get__rewards(self):
        """ Property getter """

        if self.rewards:
            return self.rewards[:]#[r for r in self.rewards]
        else:
            return [0]

    #--------------------------------------------------------------------------
    #  Public interface
    #--------------------------------------------------------------------------

#    def set_initial_state(self, state):
#        self.old_state = state
#        self.current_state = state
#
#
#    def new_episode(self):
#        self.reward = 0
#        self.last_action = None
#        self.old_state = None
#        if self.algorithm is not None:
#            self.algorithm.new_episode()
#
#
#    def get_action_list(self):
#        return self.current_state.get_action_list()
#
#
#    def act(self):
#        return self.apply_action(self.choose())
#
#
#    def explain_values(self):
#        print self.algorithm
#
#
#    def extract_dataset(self):
#        return self.algorithm.extract_dataset()

# EOF -------------------------------------------------------------------------
