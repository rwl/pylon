__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the discrete Temporal Difference
Reinforcement Learning algorithms (SARSA, Q, Q(lambda)) in a partially
observable MDP energy market task. """

import sys
import logging
import time
import pylab
import scipy

from pylon import Case, Bus, Generator

from pylon.pyreto import \
    MarketExperiment, ParticipantEnvironment, SmartMarket, DiscreteTask

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased import ActionValueTable#, ActionValueNetwork
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.tools.plotting import MultilinePlotter

# Set up the logger.
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler) #remove pybrain
handler = logging.FileHandler("/tmp/pylon.log", mode="wb")
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

# Define a case with two generators of differing capacity and a fixed load.
bus1 = Bus(p_demand=80.0)
g1 = Generator(bus1, p_max=60.0, p_min=0.0,
               pwl_points=[(0.0, 0.0), (60.0, 600.0)])
g2 = Generator(bus1, p_max=100.0, p_min=0.0,
               pwl_points=[(0.0, 0.0), (100.0, 500.0)])
case = Case(buses=[bus1], generators=[g1, g2])

# Create the market and associate learning agents with each generator.
mkt = SmartMarket(case)
dim_state, num_actions = (10, 10)

env1 = ParticipantEnvironment(g1, mkt)
task1 = DiscreteTask(env1, dim_state, num_actions)
module1 = ActionValueTable(dim_state, num_actions)
module1.initialize(1.0)
learner1 = SARSA() #Q() QLambda()
#learner1.explorer = BoltzmannExplorer() # default is e-greedy.
agent1 = LearningAgent(module1, learner1)

env2 = ParticipantEnvironment(g2, mkt)
task2 = DiscreteTask(env2, dim_state, num_actions)
module2 = ActionValueTable(dim_state, num_actions)
module2.initialize(1.0)
agent2 = LearningAgent(module2, SARSA())

exp = MarketExperiment([task1, task2], [agent1, agent2], mkt)

# Prepare for plotting.
pylab.figure()
pylab.ion()
pl = MultilinePlotter(autoscale=1.2, xlim=[0, 24], ylim=[0, 1])
pl.setLineStyle(linewidth=2)
pl.setLegend([agent1.name], loc='upper right')

# Execute interactions with the enironment in batch mode.
t0 = time.time()
x = 0
batch = 24
while x < 240:
    x += batch
    exp.doInteractions(batch)

    # Plot the progress of the agents.
#    pylab.clf()
#    pylab.plot(agent1.module.params, "mx-")
#    pylab.plot(agent2.module.params, "ro-")
#    pylab.draw()

    reward = scipy.mean(agent1.history.getSumOverSequences('reward'))
    pl.addData(0, x, reward)
    pl.update()

    agent1.learn()
    agent1.reset()
    agent2.learn()
    agent2.reset()

pl.show("Periods", "Reward", "Value-based Reward", popup=True)

logger.info("Example completed in %.3fs" % (time.time() - t0))

time.sleep(6)
