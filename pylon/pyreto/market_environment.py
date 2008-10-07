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

""" """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import \
    HasTraits, Int, Instance, List, Float, Bool,  Button, Property, \
    cached_property, on_trait_change, Range

from enthought.traits.ui.api import \
    View, Group, Item, DropEditor, DNDEditor, HGroup, VGroup

from enthought.pyface.image_resource import ImageResource

from pyqle.environment.environment import Environment

from pylon.pyreto.market_state import MarketState

from pylon.api import Network, Generator, Load
from pylon.routine.api import DCOPFRoutine
from pylon.ui.plot.actions_plot import ActionsPlot
from pylon.ui.plot.rewards_plot import RewardsPlot
from pylon.ui.plot.colours import dark, light

#------------------------------------------------------------------------------
#  Setup a logger for this module:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "MarketEnvironment" class:
#------------------------------------------------------------------------------

class MarketEnvironment(Environment):
    """ """

    #--------------------------------------------------------------------------
    #  "MarketEnvironment" interface:
    #--------------------------------------------------------------------------

    # The playing field
    network = Instance(Network)

    # The number of trading periods
    periods = Range(1, 999, auto_set=False, mode="spinner")

    # Puts the environment into the initial state
    start = Button("Initiate")

    # A plot of all actions performed
    actions_plot = Instance(ActionsPlot, transient=True)

    # A plot of all computed rewards
    rewards_plot = Instance(RewardsPlot, transient=True)

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    # The state which the environment will be put into when initialised:
    initial_state = Instance(MarketState)

    # The current state of the environment:
    state = Instance(MarketState)

    # Composed reward for the previous action:
    reward = List(Float)

    # True if the environment has reached the final state:
    is_final = Property(Bool(False), depends_on=["state"])

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        HGroup(
            Group(
                Item(
                    name="network", style="readonly",
                    editor=DropEditor(klass=Network),
                    show_label=False
                ),
                Group(Item(name="network", style="simple", show_label=False)),
                "_",
                Item(name="name", style="simple"),
                Item(name="periods"),
                Group(Item(name="start", style="simple", show_label=False)),
        #        Item(name="is_final", style="readonly"),
            ),
            "_",
            VGroup(
                Item(name="actions_plot", show_label=False, style="custom"),
                Item(name="rewards_plot", show_label=False, style="custom")
            )
        ),
        id="pylon.pyreto.market_environment_view",
        resizable=True,
        width = .3
    )

    #--------------------------------------------------------------------------
    #  "MarketEnvironment" interface:
    #--------------------------------------------------------------------------

    def _actions_plot_default(self):
        """ Trait initialiser """

        return ActionsPlot(environment=self)


    def _rewards_plot_default(self):
        """ Trait initialiser """

        return RewardsPlot(environment=self)


    def _start_fired(self):
        """ The participant swarm listens for the state change """

        logger.debug(
            "Setting initial market [%s] state [%s]" %
            (self.name, self.initial_state)
        )

        self.state = self.initial_state

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def _initial_state_default(self):
        """ Trait initialiser """

        return MarketState(environment=self, period=1)


    def apply_action(self, composed_action):
        """ Computes the next state, given the current state and a
        list of actions

        """

        if self.network is None:
            logger.error("Market environment contains no Network")
            return []

        generators = self.network.in_service_generators
        loads = self.network.in_service_loads
        n_buses = self.network.n_non_islanded_buses
        n_generators = self.network.n_in_service_generators

        self.actions_plot.update_action_plot(composed_action)

        # Perform the supply actions on the environment
        for action in composed_action:
            if isinstance(action.asset, Generator):
                # FIXME: We have to find the generator using the id trait since
                # post-pickling the asset trait of the participant environment
                # is to a different generator object than that which exists
                # in the network.
                for generator in generators:
                    if generator.id == action.asset.id:
                        break
                generator.p_max = action.value

            elif isinstance(action.asset, Load):
                for load in loads:
                    if load.id == action.asset.id:
                        break
                load.p = action.value

            else:
                raise ValueError

        # Run the routine using demand from the previous period
        routine = DCOPFRoutine(network=self.network)
        solution = routine.solve()
        del routine

        # Extract the despatched generator outputs
        if solution["x"] is not None:
            p_despatch = solution["x"][n_buses:n_buses+n_generators]
            logger.debug("Generators despatched at:\n%s" % (p_despatch))
        else:
            logger.info("No solution found in period %d" % self.state.period)
            p_despatch = [0]*n_generators

        # Sort rewards
        rewards = []
        for action in composed_action:
            if isinstance(action.asset, Generator):
                g = action.asset
                # Find generator using id
                for g_idx, generator in enumerate(generators):
                    if generator.id == g.id:
                        break

                # The reward is the product of the output and cost
                g_reward = p_despatch[g_idx] * generator.p_cost
                rewards.append(g_reward)
            else:
                # Zero reward for loads
                rewards.append(0.0)

        logger.debug(
            "Market [%s] determined agent rewards: %s" % (self.name, rewards)
        )

        if rewards == self.reward:
            self.reward = rewards
            # Force agents to learn for identical reward
            self.trait_property_changed("reward", self.reward, rewards)
        else:
            self.reward = rewards


#    def successor_state(self):
#        """ Computes the successor state """

        if not self.is_final:
            logger.debug(
                "Environment [%s] determining successor state" % self.name
            )
            successor_state = self.state.copy()
            successor_state.period += 1
#            successor_state.demand = sum([l.p for l in loads])
            self.state = successor_state
        else:
            logger.debug("Environment entered FINAL state!")
            self.state = None


    def _get_action_list(self, event):
        """ The list of possible actions is given by each elementary
        agents local environment

        """

        return None


#    @cached_property
    def _get_is_final(self):
        """ Determines if the new state is the final state """

        if self.state is not None:
            if self.state.period == self.periods:
                return True
            else:
                return False
        else:
            return False


    def _get_winner(self):
        """ Property getter """

        pass


# EOF -------------------------------------------------------------------------
