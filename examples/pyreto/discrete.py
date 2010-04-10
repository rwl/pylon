__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how Pyreto can simulate a discrete representation
of a power exchange auction market. """

import sys
import logging
import pylon
import pyreto

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.learners import Q

logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler) # rm pybrain
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

case = pylon.Case.load("../data/case6ww.pkl")

market = pyreto.SmartMarket(case, priceCap=100.0)

# Define a non-learning agent.
env1 = pyreto.DiscreteMarketEnvironment([case.generators[0],
                                         case.generators[1]], market)
task1 = pyreto.ProfitTask(env1)
agent1 = LearningAgent(ActionValueTable(1, 1))

# Define a learning agent.
env2 = pyreto.DiscreteMarketEnvironment([case.generators[2]], market,
                                        outdim=10, numOffbids=2,
                                        markups=(0.1, 0.2, 0.33, 0.5))
task2 = pyreto.ProfitTask(env2)
module2 = ActionValueTable(numStates=10, numActions=2*4)
agent2 = LearningAgent(module2, Q())

experiment = pyreto.MarketExperiment([task1, task2], [agent1, agent2], market)

x = 0
batch = 2
while x <= 1000:
    experiment.doInteractions(batch)
    for agent in experiment.agents:
        agent.learn()
        agent.reset()
    x += batch
