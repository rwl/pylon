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

from enthought.traits.api import HasTraits, Int, List, Instance, Button
from enthought.traits.ui.api import View, Group, Item

from pybrain.rl.experiments import Experiment, EpisodicExperiment

from pylon.api import Network
from pylon.routine.api import DCOPFRoutine

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

    step = Button

    #--------------------------------------------------------------------------
    #  View definitions:
    #--------------------------------------------------------------------------

    traits_view = View( Item( name       = "power_sys",
                              show_label = False,
                              style      = "custom" ),
                        Item( name       = "step",
                              show_label = False ),
                        id        = "pylon.pybrain.experiment",
                        title     = "Market Experiment",
                        resizable = True,
                        buttons   = [ "OK" ] )

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
        self.doInteractions( number = 1 )

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
                task.performAction( agent.getAction() )

            # Optimise the power system model.
            routine  = DCOPFRoutine(self.power_sys, show_progress=False)
            solution = routine.solve()

            if solution["status"] != "optimal":
                print "NO OPTIMAL SOLUTION FOR INTERACTION %d." % interaction
#                break

            # Reward each agent appropriately.
            for i, agent in enumerate(self.agents):
                task   = self.tasks[i]
                reward = 0.0#task.getReward()
                agent.giveReward(reward)

            # Update each agent's environment state attributes.
            for task in self.tasks:
                demand = sum([l.p for l in self.power_sys.in_service_loads])
                task.env.demand = demand
                # TODO: Implement computation of MCP and demand forecast.
                task.env.mcp      = 0.0
                task.env.forecast = demand

        ret = []
        for agent in self.agents:
            rewards = []
            for n in range(agent.history.getNumSequences()):
                returns = agent.history.getSequence(n)
                state   = returns[0]
                action  = returns[1]
                reward  = returns[2]
                rewards.append( reward )#sum(reward, 0).item() )
            ret.append(rewards)

        print "REWARDS:", ret

        return ret

# EOF -------------------------------------------------------------------------
