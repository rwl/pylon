__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how Pyreto can simulate a discrete representation
of a power exchange auction market. """

import sys
import logging
import pylab

from scipy import array

import pylon
import pyreto.discrete
import pyreto.continuous
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
case.generators[1].p_cost = (0.0, 6.5, 200.0)
case.generators[2].p_cost = (0.0, 2.0, 200.0)

case.generators[0].c_shutdown = 100.0

#case.generators[0].p_min = 0.0 # TODO: Unit-decommitment.
#case.generators[1].p_min = 0.0
##case.generators[2].p_min = 0.0

case.generators[0].p_max = 100.0
case.generators[1].p_max = 70.0
case.generators[2].p_max = 70.0

#pyreto.util.plotGenCost(case.generators)

# Create a power exchange auction market and specify a price cap.
market = pyreto.SmartMarket(case, priceCap=100.0, decommit=False)

# Define a 24-hour load profile with hourly values.
#p1h = [0.52, 0.54, 0.52, 0.50, 0.52, 0.57, 0.60, 0.71, 0.89, 0.85, 0.88, 0.94,
#       0.90, 0.88, 0.88, 0.82, 0.80, 0.78, 0.76, 0.68, 0.68, 0.68, 0.65, 0.58]
#p1h = p1h[2::4]
p1h = array([0.9])#, 0.6]

# Create an empty multi-agent experiment and then populate it.
experiment = pyreto.continuous.MarketExperiment([], [], market, p1h)

# A participant may submit any number of offers/bids for each of the
# generators in its portfolio.
nOffer = 1

nStates = 3

# Associate a learning agent with the first generator.
env = pyreto.discrete.MarketEnvironment(case.generators[:1], market,
                                        numStates=nStates, numOffbids=nOffer,
                                        markups=(20, 75), withholds=(0, 50))
task = pyreto.discrete.ProfitTask(env, maxSteps=len(p1h))

#print env.outdim, len(env._allActions), env.numOffbids * len(env.generators) * len(env.markups)

nActions = len(env._allActions)
module = ActionValueTable(numStates=nStates, numActions=nActions)

learner = Q()
#learner = QLambda()
#learner = SARSA(gamma=0.8)
#learner.explorer = BoltzmannExplorer()#tau=100, decay=0.95)

##learner = pyreto.roth_erev.RothErev(experimentation=0.55, recency=0.3)
#learner = pyreto.roth_erev.VariantRothErev(experimentation=0.55, recency=0.3)
#learner.explorer = BoltzmannExplorer(epsilon=100.0, decay=0.9995)

agent = LearningAgent(module, learner)
experiment.tasks.append(task)
experiment.agents.append(agent)

# Define a non-learning agent that will bid maximum power at marginal cost.
env2 = pyreto.discrete.MarketEnvironment(case.generators[1:], market, nOffer)
task2 = pyreto.discrete.ProfitTask(env2, maxSteps=len(p1h))
agent2 = pyreto.util.ZeroAgent(env2.outdim, env2.indim)
experiment.tasks.append(task2)
experiment.agents.append(agent2)

# Prepare plotting.
pylab.gray()
pylab.ion()

weeks = 208 # number of roleouts
days = 1 # number of samples per learning step
for week in range(weeks):
    experiment.doEpisodes(days)

    for agent in experiment.agents:
        print agent.history["action"]
        print agent.history["reward"]

        agent.learn()
        agent.reset()

#    print "PARAM:",experiment.agents[0].module.params.reshape(nStates,nActions)
#    print experiment.agents[0].module.params.reshape(nStates,nActions).max(1)

    # Draw the table for agent 1.
    pylab.pcolor(module.params.reshape(nStates,nActions))
    pylab.draw()
