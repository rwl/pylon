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

from pylon.readwrite import ReSTWriter

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "MarketExperiment" class:
#------------------------------------------------------------------------------

class MarketExperiment(object):
    """ Defines an experiment that matches up agents with tasks and handles
        their interaction.
    """
    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, tasks, agents, market):
        """ Initialises the market experiment.
        """
        assert len(tasks) == len(agents)

        # Tasks associate and agent with its environment.
        self.tasks = tasks

        # Agents capable of producing actions based on previous observations.
        self.agents = agents

        # Market to which agents submit offers/bids.
        self.market = market

        self.stepid = 0

    #--------------------------------------------------------------------------
    #  PyBrain "Experiment" interface:
    #--------------------------------------------------------------------------

    def doInteractions(self, number=1):
        """ Directly maps the agents and the tasks.
        """
        for interaction in range(number):
            # Initialise the market.
            self.market.init()

            # Get an action from each agent and perform it.
            for task, agent in zip(self.tasks, self.agents):

                self.stepid += 1
                observation = task.getObservation()
#                logger.debug("Agent [%s] integrating observation: %s" %
#                             (agent.name, observation))
                agent.integrateObservation(observation)

                action = agent.getAction()
#                logger.debug("Agent [%s] performing action: %s" %
#                             (agent.name, action))
                task.performAction(action)


            # Clear the market.
            self.market.clear()


            # Reward each agent appropriately.
            for task, agent in zip(self.tasks, self.agents):

                reward = task.getReward()
#                logger.debug("Agent [%s] receiving reward: %s" %
#                             (agent.name, reward))

                if task.env.hasRenderer():
                    data = (None, None, reward[0], None)
                    task.env.getRenderer().updateData(data, False)

                agent.giveReward(reward)

            # Instruct each agent to learn from it's actions.
            for agent in self.agents:
#                logger.debug("Agent [%s] being instructed to learn." %
#                             agent.name)
                agent.learn()

#                logger.debug("Module [%s] parameters: %s" %
#                             (agent.module.name, agent.module.params))

                if task.env.hasRenderer():
                    data = (None, None, None, agent.module.params[0])
                    task.env.getRenderer().updateData(data)

            # Update each agent's environment state attributes.
#            for task in self.tasks:
#                demand = sum([l.p for l in self.power_system.online_loads])
#                task.env.demand = demand
#                # TODO: Implement computation of MCP and demand forecast.
#                task.env.mcp      = 0.0
#                task.env.forecast = demand


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

# EOF -------------------------------------------------------------------------
