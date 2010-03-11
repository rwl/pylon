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

#from pybrain.rl.experiments import Experiment, EpisodicExperiment
from pybrain.rl.agents.optimization import OptimizationAgent

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

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
        super(MarketExperiment, self).__init__(None, None)

        assert len(tasks) == len(agents)

        # Tasks associate and agent with its environment.
        self.tasks = tasks

        # Agents capable of producing actions based on previous observations.
        self.agents = agents

        # Market to which agents submit offers/bids.
        self.market = market

        self.stepid = 0

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

        return self.stepid


    def _oneInteraction(self):
        """ Coordinates one interaction between each agent and its environment.
        """
        self.stepid += 1

        logger.info("Entering simulation period %d." % self.stepid)

        # Initialise the market.
        self.market.reset()

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

        logger.info("")


    def reset(self):
        """ Sets initial conditions for the experiment.
        """
        self.stepid = 0

        for task, agent in zip(self.tasks, self.agents):
            task.env.reset()

            agent.module.reset()
            agent.history.reset()
#            agent.history.clear()

#------------------------------------------------------------------------------
#  "EpisodicMarketExperiment" class:
#------------------------------------------------------------------------------

class EpisodicMarketExperiment(object):
    """ Defines a multi-agent market experiment in which loads follow an
        episodic profile.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, tasks, agents, market, profile=None):
        """ Initialises the market experiment.
        """
        super(EpisodicMarketExperiment, self).__init__(None, None)

        assert len(tasks) == len(agents)

        # Tasks associate and agent with its environment.
        self.tasks = tasks

        # Agents capable of producing actions based on previous observations.
        self.agents = agents

        # Market to which agents submit offers/bids.
        self.market = market

        # Load profile.
        self.profile = [1.0] if profile is None else profile

        self.do_optimisation = {}
        self.optimisers = {}

        for task, agent in zip(self.tasks, self.agents):
            if isinstance(agent, OptimizationAgent):
                self.do_optimisation[agent] = True
                self.optimisers[agent] = agent.learner
                self.optimisers[agent].setEvaluator(task, agent.module)
                self.optimisers[agent].maxEvaluations = \
                    self.optimisers[agent].numEvaluations
            else:
                self.do_optimisation[agent] = False

    #--------------------------------------------------------------------------
    #  "Experiment" interface:
    #--------------------------------------------------------------------------

    def _oneInteraction(self):
        """ Coordinates one interaction between each agent and its environment.
        """
        self.stepid += 1

        logger.info("Entering simulation period %d." % self.stepid)

        # Initialise the market.
        self.market.reset()

        # Get an action from each agent and perform it.
        for task, agent in zip(self.tasks, self.agents):
            if self.do_optimisation[agent]:
                raise Exception("When using a black-box learning algorithm, "
                                "only full episodes can be done.")
            if not task.isFinished():
                observation = task.getObservation()
                agent.integrateObservation(observation)

                action = agent.getAction()
                task.performAction(action)

        # Clear the market.
        self.market.run()

        # Reward each agent appropriately.
        for task, agent in zip(self.tasks, self.agents):
            if not task.isFinished():
                reward = task.getReward()
                agent.giveReward(reward)


    def reset(self):
        """ Sets initial conditions for the experiment.
        """
        self.stepid = 0

        for task, agent in zip(self.tasks, self.agents):
            task.env.reset()

            agent.module.reset()
            agent.history.reset()

    #--------------------------------------------------------------------------
    #  "EpisodicExperiment" interface:
    #--------------------------------------------------------------------------

    def doEpisodes(self, number=1):
        """ Do the given numer of episodes, and return the rewards of each
            step as a list.
        """
        for _ in range(number):
            for task, agent in zip(self.tasks, self.agents):
                agent.newEpisode()
                task.reset()
            while False in [task.isFinished() for task in self.tasks]:
                self._oneInteraction()

# EOF -------------------------------------------------------------------------
