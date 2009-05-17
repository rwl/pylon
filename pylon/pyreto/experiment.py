#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" Defines an experiment that matches up agents with tasks and handles their
    interaction.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
from numpy import array, zeros

from enthought.traits.api \
    import HasTraits, Int, List, Instance, Button, Range, Str, on_trait_change

from enthought.traits.ui.api import View, Group, Item, HGroup, VGroup, spring

from pybrain.rl.experiments import Experiment, EpisodicExperiment

from pylon.api import Network
from pylon.routine.api import DCOPFRoutine
from pylon.ui.routine.dc_opf_view_model import DCOPFViewModel
from pylon.ui.plot.rewards_plot import RewardsPlot
from pylon.readwrite.rst_writer import ReSTWriter

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "MarketExperiment" class:
#------------------------------------------------------------------------------

class MarketExperiment ( HasTraits ):
    """ Defines an experiment that matches up agents with tasks and handles
        their interaction.
    """

    name = Str

    stepid = 0

    tasks = list

    # Agents capable of producing actions based on previous observations.
    agents = list

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The power system model containing the agent's assets.
    power_system = Instance( Network )

    # Routine for solving the OPF problem.
    routine = Instance( HasTraits )

    # Perform interactions.
    step = Button

    # Number of interactions to perfrom.
    steps = Range(1, 100, auto_set=False, mode="spinner",
                  desc="number of interactions to perform")

    # Set initial conditions.
    reset_experiment = Button("Reset", desc="set initial conditions")

    #--------------------------------------------------------------------------
    #  Plot definitions:
    #--------------------------------------------------------------------------

    # Plot of environment state.
    state_plot = Instance(RewardsPlot, transient=True)

    # Plot of agent actions.
    actions_plot = Instance(RewardsPlot, transient=True)

    # Plot of agent rewards.
    rewards_plot = Instance(RewardsPlot, transient=True)

    #--------------------------------------------------------------------------
    #  View definitions:
    #--------------------------------------------------------------------------

    traits_view = View(
        VGroup(VGroup(Item("state_plot", show_label=False, style="custom"),
                      Item("actions_plot", show_label=False, style="custom"),
                      Item("rewards_plot", show_label=False, style="custom")
                      ),
               HGroup(Item("power_system", show_label=False, style="simple",
                           width=200),
                      Item("routine", show_label=False, style="simple",
                           width=150),
                      Item("steps", width=100),
                      Item("step", show_label=False, width=150),
                      Item("reset_experiment", show_label=False, width=100))),
        id        = "pylon.pyreto.experiment",
        title     = "Market Experiment",
        resizable = True,
        buttons   = ["OK"]
    )

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, tasks, agents, power_system, *kw, **kw_args):
        """ Initialises the market experiment.
        """
        super(MarketExperiment, self).__init__(task=None, agent=None, *kw,
                                               **kw_args)
        assert len(tasks) == len(agents)

        self.tasks = tasks
        self.agents = agents
        self.stepid = 0

        self.power_system = power_system


    def _routine_default(self):
        """ Trait initialiser.
        """
        return DCOPFViewModel(network=self.power_system, show_progress=False)
#        return DCOPFRoutine(self.power_system, show_progress=False)


    def _state_plot_default(self):
        """ Trait initialiser.
        """
        return RewardsPlot(title="State", index_label="Time",
                                           value_label="Value")


    def _actions_plot_default(self):
        """ Trait initialiser.
        """
        return RewardsPlot(title="Action", index_label="Time",
                                           value_label="Currency")


    def _rewards_plot_default(self):
        """ Trait initialiser.
        """
        rewards_plot = RewardsPlot(title="Reward", index_label="Time",
                                           value_label="Currency")

        return rewards_plot

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    def _step_fired(self):
        """ Handles the 'step' button event.
        """
        self.doInteractions( number = self.steps )


    def _power_system_changed(self, new):
        """ Handles new power system.
        """
        if new is not None:
            self.routine.network = new

    #--------------------------------------------------------------------------
    #  "Experiment" interface:
    #--------------------------------------------------------------------------

    def doInteractions(self, number=1):
        """ Directly maps the agents and the tasks.
        """
        for interaction in range(number):
            # Perform action for each agent.
            for i, agent in enumerate(self.agents):
                task = self.tasks[i]

                self.stepid += 1
                observation = task.getObservation()
                logger.debug("Agent [%s] integrating observation: %s" %
                             (agent.name, observation))
                agent.integrateObservation( observation )

                action = agent.getAction()
                logger.debug("Agent [%s] performing action: %s" %
                             (agent.name, action))
                task.performAction( action )


            writer = ReSTWriter(self.power_system, sys.stdout)
            writer.write_generator_data()

            # Optimise the power system model.
            solution = self.routine.solve()
#            self.routine.edit_traits(kind="livemodal")

            writer.write_generator_data()

            if solution["status"] != "optimal":
                logger.debug("No solution for interaction: %d" % interaction)
                if logger.handlers:
                    stream = logger.handlers[0].stream
                else:
                    stream = sys.stdout
                writer = ReSTWriter(self.power_system, stream)
                writer.write_generator_data()

            # Reward each agent appropriately.
            for i, agent in enumerate(self.agents):
                task   = self.tasks[i]
                reward = task.getReward()
                logger.debug("Agent [%s] receiving reward: %s" %
                             (agent.name, reward))
                agent.giveReward( reward )

            # Instruct each agent to learn from it's actions.
            for agent in self.agents:
                logger.debug("Agent [%s] being instructed to learn." %
                             agent.name)
                agent.learn()

                logger.debug("Module [%s] parameters: %s" %
                             (agent.module.name, agent.module.params))

            # Update each agent's environment state attributes.
#            for task in self.tasks:
#                demand = sum([l.p for l in self.power_system.online_loads])
#                task.env.demand = demand
#                # TODO: Implement computation of MCP and demand forecast.
#                task.env.mcp      = 0.0
#                task.env.forecast = demand

            self._update_plots()


    def _update_plots(self):
        """ Updates plot data.
        """
        all_states = []
        all_actions = []
        all_rewards = []

#            if self.agents:
#                n_seq = self.agents[0].history.getNumSequences()
#                print "N_SEQUENCES:", n_seq
#                all_rewards = zeros(shape=(len(self.agents), n_seq))
#            else:
#                n_seq = 0
#                all_rewards = array([])

        for j, agent in enumerate(self.agents):
            observations = agent.history.getField("state")
            all_states.append(observations.transpose())

            actions = agent.history.getField("action")
            all_actions.append(actions.transpose())

            rewards = agent.history.getField("reward")
            all_rewards.append(rewards.transpose())

#                print "REWARDS:", rewards
#                print "SIZE:", rewards.shape
#                print "ALL SIZE:", all_rewards.shape
#                all_rewards[j, :] = rewards.transpose()

#                rewards = zeros(shape=(n_seq))
#                for n in range(agent.history.getNumSequences()):
#                    returns = agent.history.getSequence(n)
#                    state   = returns[0]
#                    action  = returns[1]
#                    reward  = returns[2]
#                    rewards[n] = reward
#                all_rewards[j,:] = rewards

        self.state_plot.set_data(all_states)
        self.actions_plot.set_data(all_actions)
        self.rewards_plot.set_data(all_rewards)


    @on_trait_change("reset_experiment")
    def reset(self):
        """ Set initial conditions.
        """
        self.stepid = 0

        for task in self.tasks:
            task.env.reset()

        for agent in self.agents:
            agent.module.reset()
            agent.history.reset()
#            agent.history.clear()

        data_names = self.rewards_plot.data.list_data()
        for data_name in data_names:#[n for n in data_names if n != "x"]:
            self.rewards_plot.data.del_data(data_name)
#        event = {"removed": data_names}
#        self.rewards_plot.data.data_changed = event

        names = self.rewards_plot.plot.plots.keys()
#        self.rewards_plot.plot.delplot(names)
        for name in names:
            self.rewards_plot.plot.delplot(name)

# EOF -------------------------------------------------------------------------
