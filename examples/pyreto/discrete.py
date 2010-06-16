__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how Pyreto can simulate a discrete representation
of a power exchange auction market. """

import sys
import logging
import pylon
import pyreto.discrete

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.learners import Q

logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler) # rm pybrain
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

# Load the electric power system model.
case = pylon.Case.load("../data/case6ww.pkl")

# Create a power exchange auction market and specify a price cap.
market = pyreto.SmartMarket(case, priceCap=100.0)

# Create an empty multi-agent experiment and then populate it.
experiment = pyreto.discrete.MarketExperiment([], [], market)

# A participant may submit any number of offers/bids for each of the
# generators in its portfolio.
nOffer = 1

# Associate a learning agent with the first generator.
env1 = pyreto.discrete.MarketEnvironment(case.generators[:1], market,
                                         numStates=10, numOffbids=nOffer,
                                         markups=(10, 20, 33, 50))
task1 = pyreto.discrete.ProfitTask(env1)
module1 = ActionValueTable(numStates=env1.outdim, numActions=env1.indim)
agent1 = LearningAgent(module1, Q())
experiment.tasks.append(task1)
experiment.agents.append(agent1)

# Define a non-learning agent that will bid maximum power at marginal cost.
env2 = pyreto.discrete.MarketEnvironment(case.generators[1:], market, nOffer)
task2 = pyreto.discrete.ProfitTask(env2)
agent2 = pyreto.util.ZeroAgent(env2.outdim, env2.indim)
experiment.tasks.append(task2)
experiment.agents.append(agent2)

x = 0
batch = 2
while x <= 1000:
    experiment.doInteractions(batch)
    for agent in experiment.agents:
        agent.learn()
        agent.reset()
    x += batch
