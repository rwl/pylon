#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Defines an experiment that matches up agents with tasks and handles their
    interaction.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging

from pybrain.rl.experiments import Experiment

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "GraphicalExperiment" class:
#------------------------------------------------------------------------------

class GraphicalExperiment(Experiment):
    """ Defines an experiment with graphical output.
    """

    def __init__(self, task, agent):
        """ Constructs a new GraphicalExperiment.
        """
        super(GraphicalExperiment, self).__init__(task, agent)
        self.renderer = None


    def setRenderer(self, renderer):
        """ Set the renderer, which is an object of or inherited from Renderer.
        """
        self.renderer = renderer


    def getRenderer(self):
        """ Returns the current renderer.
        """
        return self.renderer


    def hasRenderer(self):
        """ Returns true if a Renderer has been previously set.
        """
        return (self.getRenderer() != None)

#------------------------------------------------------------------------------
#  "MarketExperiment" class:
#------------------------------------------------------------------------------

class MarketExperiment(GraphicalExperiment):
    """ Defines an experiment that matches up agents with tasks and handles
        their interaction.
    """
    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, tasks, agents, market):
        """ Initialises the market experiment.
        """
        super(MarketExperiment, self).__init__(None, None)

        assert len(tasks) == len(agents)

        # Tasks associate and agent with its environment.
        self.tasks = tasks

        # Agents capable of producing actions based on previous observations.
        self.agents = agents

        # Market to which agents submit offers/bids.
        self.market = market

        self.stepid = 0


    def _oneInteraction(self):
        """ Coordinates one interaction between each agent and its environment.
        """
        self.stepid += 1

        logger.info("Entering period %d." % self.stepid)

        # Initialise the market.
        self.market.init()

        # Get an action from each agent and perform it.
        for task, agent in zip(self.tasks, self.agents):
            observation = task.getObservation()
            agent.integrateObservation(observation)

            action = agent.getAction()
            task.performAction(action)


        # Clear the market.
        self.market.run()


        # Reward each agent appropriately.
        for task, agent in zip(self.tasks, self.agents):
            reward = task.getReward()
            agent.giveReward(reward)

        # Instruct each agent to learn from it's actions.
#        for agent in self.agents:
#            agent.learn()

        # Update environment rendering data.
#        for task, agent in zip(self.tasks, self.agents):
#            if task.env.hasRenderer():
#                numseq = agent.history.getNumSequences()
#                seq = agent.history.getSequence(numseq - 1)
#                states = seq[0][-1]
#                actions = seq[1][-1]
#                rewards = seq[2][-1]
#                task.env.getRenderer().updateData(states, actions, rewards)

        logger.info("")

    #--------------------------------------------------------------------------
    #  "Experiment" interface:
    #--------------------------------------------------------------------------

    def doInteractions(self, number=1):
        """ Directly maps the agents and the tasks.
        """
#        if self.hasRenderer():
#            self.getRenderer().start()

        t0 = time.time()

        for _ in range(number):
            self._oneInteraction()

        elapsed = time.time() - t0
        logger.info("%d interactions executed in %.3fs." % (number, elapsed))

        # Update experiment rendering data.
        if self.hasRenderer():
            data = []
            for agent in self.agents:
                nseq = agent.history.getNumSequences()
                seq = agent.history.getSequence(nseq - 1)
                data.append(seq)

            self.getRenderer().updateData(data)

#        if self.hasRenderer():
#            self.getRenderer().stop()

    #--------------------------------------------------------------------------
    #  Set initial conditions for the experiment:
    #--------------------------------------------------------------------------

    def reset(self):
        """ Sets initial conditions for the experiment.
        """
        self.stepid = 0

        for task, agent in zip(self.tasks, self.agents):
            task.env.reset()

            agent.module.reset()
            agent.history.reset()
#            agent.history.clear()

# EOF -------------------------------------------------------------------------
