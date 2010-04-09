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

""" Defines a test case for the Pyreto market experiment.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
import unittest

from os.path import dirname, join

from pylon import Case, Bus, Generator
from pylon.readwrite import PickleReader

from pyreto import \
    MarketExperiment, DiscreteMarketEnvironment, SmartMarket, \
    ProfitTask, EpisodicProfitTask, RothErev, PropensityTable

from pyreto.renderer import ParticipantRenderer, ExperimentRenderer

from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import ENAC
from pybrain.rl.learners.valuebased import ActionValueTable, ActionValueNetwork
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "t_auction_case.pkl")

#------------------------------------------------------------------------------
#  Returns a test power system:
#------------------------------------------------------------------------------

def getPickledCase():
    """ Returns a test power system case.
    """
    # Read case from data file.
    return Case.load(DATA_FILE)


def get1Bus():
    """ Returns a simple one bus case.
    """
    bus1 = Bus(name="Bus1", p_demand=80.0)

    g1 = Generator(bus1, name="G1", p_max=60.0, p_min=0.0)
    g2 = Generator(bus1, name="G2", p_max=100.0, p_min=0.0)

    return Case(name="1Bus", buses=[bus1], generators=[g1, g2])

#------------------------------------------------------------------------------
#  "MarketExperimentTest" class:
#------------------------------------------------------------------------------

class MarketExperimentTest(unittest.TestCase):
    """ Defines a test case for the Pyreto market experiment.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
#        self.case = get1Bus()
        self.case = getPickledCase()


#    def testStateless(self):
#        """ Test learning without state information.
#        """
#        mkt = SmartMarket(self.case)
#        exp = MarketExperiment([], [], mkt)
#        for g in self.case.generators:
#            env = ParticipantEnvironment(g, mkt)
#            exp.tasks.append(Discretetask(env))
#            table = ActionValueTable(1, 4)
##            table = PropensityTable(4, actionDomain)
#            table.initialize(1.0)
#            exp.agents.append(LearningAgent(table, RothErev()))
#        exp.doInteractions(3)


    def testValueBased(self):
        """ Test value-based learner.
        """
        mkt = SmartMarket(self.case)
        exp = MarketExperiment([], [], mkt)
        for g in self.case.generators:
            env = DiscreteMarketEnvironment([g], mkt)
            dim_state, num_actions = (10, 10)
            exp.tasks.append(ProfitTask(env, dim_state, num_actions))
            module = ActionValueTable(dim_state, num_actions)
            module.initialize(1.0)
#            module = ActionValueNetwork(dimState=1, numActions=4)
            learner = SARSA() #Q() QLambda()
#            learner.explorer = BoltzmannExplorer() # default is e-greedy.
            exp.agents.append(LearningAgent(module, learner))
        for _ in range(1000):
            exp.doInteractions(24) # interact with the env in batch mode
            for agent in exp.agents:
                agent.learn()
                agent.reset()


#    def testContinuous(self):
#        """ Test learning with continous sensor and action spaces.
#        """
#        mkt = SmartMarket(self.case)
#
#        agents = []
#        tasks = []
#        for g in self.case.generators:
#            # Create an environment for the agent with an asset and a market.
#            env = ParticipantEnvironment(g, mkt, numOffbids=2)
##            env.setRenderer(ParticipantRenderer(env.outdim, env.indim))
##            env.getRenderer().start()
#
#            # Create a task for the agent to achieve.
#            task = ContinuousTask(env)
#
#            # Build an artificial neural network for the agent.
#            net = buildNetwork(task.outdim, task.indim, bias=False,
#                               outputbias=False)
##            net._setParameters(array([9]))
#
#            # Create a learning agent with a learning algorithm.
#            agent = LearningAgent(module=net, learner=ENAC())
#            # initialize parameters (variance)
##            agent.setSigma([-1.5])
#            # learning options
#            agent.learner.alpha = 2.0
#            # agent.learner.rprop = True
#            agent.actaspg = False
#    #        agent.disableLearning()
#
#            agents.append(agent)
#            tasks.append(task)
#
#        experiment = MarketExperiment(tasks, agents, mkt)
#        experiment.setRenderer(ExperimentRenderer())
#
#        # Experiment event sequence:
#        #   task.getObservation()
#        #     env.getSensors()
#        #     task.normalize()
#        #   agent.integrateObservation()
#        #     Stores the observation received in a temporary variable until
#        #     action is called and reward is given.
#        #   agent.getAction()
#        #     module.activate(lastobs)
#        #   task.performAction()
#        #     task.denormalize(action)
#        #     env.performAction(action)
#        #   task.getReward()
#        #   agent.giveReward()
#        #   agent.learn()
#        experiment.doInteractions(3)
#
##        env.getRenderer().stop()
#
##        self.assertAlmostEqual(g1.p_cost[1], 20.0, places=2)


if __name__ == "__main__":
#    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#        format="%(levelname)s: %(message)s")

    opf_logger = logging.getLogger('pylon.opf')
    opf_logger.setLevel(logging.INFO)
    y_logger = logging.getLogger('pylon.y')
    y_logger.setLevel(logging.INFO)

    logger = logging.getLogger()

    # Remove PyBrain handlers.
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
