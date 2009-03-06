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

from numpy import array, zeros

from enthought.traits.api import HasTraits, Int, List, Instance, Button, Range
from enthought.traits.ui.api import View, Group, Item, HGroup

from pybrain.rl.experiments import Experiment, EpisodicExperiment

from pylon.api import Network
from pylon.routine.api import DCOPFRoutine
from pylon.ui.plot.rewards_plot import RewardsPlot

#------------------------------------------------------------------------------
#  "MarketExperiment" class:
#------------------------------------------------------------------------------

class MarketExperiment ( HasTraits ):
    """ Defines an experiment that matches up agents with tasks and handles
        their interaction.
    """

    stepid = 0

    tasks = list

    # Agents capable of producing actions based on previous observations.
    agents = list

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The power system model containing the agent's assets.
    power_sys = Instance( Network )

    # Perform interactions.
    step = Button

    # Number of interactions to perfrom.
    steps = Range(1, 999, auto_set=False, mode="spinner",
                  desc="number of interactions to perfrom")

    # Plot of agent rewards.
    rewards_plot = Instance(RewardsPlot, RewardsPlot(title="Rewards"))

    # Plot of agent actions.
    actions_plot = Instance(RewardsPlot, RewardsPlot(title="Actions"))

    #--------------------------------------------------------------------------
    #  View definitions:
    #--------------------------------------------------------------------------

    traits_view = View(
        Item("power_sys", show_label=False, style="simple" ),
        HGroup(Item("rewards_plot", show_label=False, style="custom"),
#               Item("actions_plot", show_label=False, style="custom")
               ),
        HGroup(Item("steps"), Item("step", show_label=False)),
        id        = "pylon.pybrain.experiment",
        title     = "Market Experiment",
        resizable = True,
        buttons   = ["OK"]
    )

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, tasks, agents, power_sys):
        """ Initialises the market experiment.
        """
        super(MarketExperiment, self).__init__(task=None, agent=None)
        assert len(tasks) == len(agents)

        self.tasks = tasks
        self.agents = agents
        self.stepid = 0

        self.power_sys = power_sys

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    def _step_fired(self):
        """ Handles the 'step' button event.
        """
        self.doInteractions( number = self.steps )

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
                agent.integrateObservation( task.getObservation() )
                action = agent.getAction()
                task.performAction( action )

            # Optimise the power system model.
            routine  = DCOPFRoutine(self.power_sys, show_progress=False)
            solution = routine.solve()

            if solution["status"] != "optimal":
                print "NO OPTIMAL SOLUTION FOR INTERACTION %d." % interaction
#                break

            # Reward each agent appropriately.
            for i, agent in enumerate(self.agents):
                task   = self.tasks[i]
                reward = task.getReward()
                agent.giveReward( reward )

            # Update each agent's environment state attributes.
            for task in self.tasks:
                demand = sum([l.p for l in self.power_sys.online_loads])
                task.env.demand = demand
                # TODO: Implement computation of MCP and demand forecast.
                task.env.mcp      = 0.0
                task.env.forecast = demand

            # Update plot data.
            all_rewards = []
            all_actions = []
#            if self.agents:
#                n_seq = self.agents[0].history.getNumSequences()
#                print "N_SEQUENCES:", n_seq
#                all_rewards = zeros(shape=(len(self.agents), n_seq))
#            else:
#                n_seq = 0
#                all_rewards = array([])

            for j, agent in enumerate(self.agents):
                rewards = agent.history.getField("reward")
                all_rewards.append(rewards.transpose())

                actions = agent.history.getField("action")
                print "AGENT ACTIONS:", actions
                all_actions.append(actions.transpose())

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

            self.rewards_plot.set_data(all_rewards)
#            self.actions_plot.set_data(all_actions)

# EOF -------------------------------------------------------------------------
