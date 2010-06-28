__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how Pyreto can simulate a discrete representation
of a power exchange auction market. """

import sys
import logging
import scipy
import pylab

import pylon
import pyreto.discrete
import pyreto.roth_erev #@UnusedImport

from pybrain.rl.agents import LearningAgent
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport

logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler) # rm pybrain
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

# Load the electric power system model.
case = pylon.Case.load("../data/case6ww.pkl")
case.generators[0].p_cost = (0.0, 5.0, 200.0)
case.generators[1].p_cost = (0.0, 7.0, 200.0)
case.generators[2].p_cost = (0.0, 2.0, 200.0)
case.generators[0].p_min = 0.0
case.generators[1].p_min = 0.0
case.generators[2].p_min = 0.0
#pyreto.util.plotGenCost(case.generators)

# Create a power exchange auction market and specify a price cap.
market = pyreto.SmartMarket(case, priceCap=100.0)

# Create an empty multi-agent experiment and then populate it.
experiment = pyreto.discrete.MarketExperiment([], [], market)

# A participant may submit any number of offers/bids for each of the
# generators in its portfolio.
nOffer = 1

nStates = 1

# Associate a learning agent with the first generator.
env = pyreto.discrete.MarketEnvironment(case.generators[:1], market,
                                        numStates=nStates, numOffbids=nOffer,
                                        markups=(10, 20, 33, 50))
task = pyreto.discrete.ProfitTask(env)

#print env.outdim, len(env._allActions), env.numOffbids * len(env.generators) * len(env.markups)

nActions = len(env._allActions)
module = ActionValueTable(numStates=nStates, numActions=nActions)

#learner = Q()
#learner = QLambda()
learner = SARSA(gamma=0.8)
#learner.explorer = BoltzmannExplorer()#tau=100, decay=0.95)

#learner = pyreto.roth_erev.RothErev(experimentation=0.55, recency=0.3)
#learner = pyreto.roth_erev.VariantRothErev(experimentation=0.55, recency=0.3)
#learner.explorer = BoltzmannExplorer(tau=100.0, decay=0.9995)

agent = LearningAgent(module, learner)
experiment.tasks.append(task)
experiment.agents.append(agent)

# Define a non-learning agent that will bid maximum power at marginal cost.
env2 = pyreto.discrete.MarketEnvironment(case.generators[1:], market, nOffer)
task2 = pyreto.discrete.ProfitTask(env2)
agent2 = pyreto.util.ZeroAgent(env2.outdim, env2.indim)
experiment.tasks.append(task2)
experiment.agents.append(agent2)

# Prepare plotting.
pylab.gray()
pylab.ion()

x = 0
batch = 4
while x <= 1000:
    experiment.doInteractions(batch)

    for agent in experiment.agents:
        agent.learn()
        agent.reset()

    print "PARAMS:", experiment.agents[0].module.params
#    print experiment.agents[0].module.params.reshape(nStates,nActions).max(1)

    # Draw the table for agent 1.
    pylab.pcolor(module.params.reshape(nStates,nActions))
    pylab.draw()

    x += batch
