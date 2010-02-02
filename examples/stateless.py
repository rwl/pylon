__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the stateless Reinforcement Learning
algorithms (Roth-Erev) in a partially observable MDP energy market task. """

import sys
import logging
import pylab
import scipy

from pylon import Case, Bus, Generator

from pylon.pyreto import MarketExperiment, ParticipantEnvironment, \
    SmartMarket, DiscreteTask, RothErev, PropensityTable

from pybrain.rl.agents import LearningAgent
from pybrain.tools.plotting import MultilinePlotter

# Set up the logger.
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler) #remove pybrain
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

# Define a single generator case with a fixed load.
bus = Bus(p_demand=80.0)
g = Generator(bus, p_max=60.0, p_min=0.0,
              p_cost=[(0.0, 0.0), (60.0, 600.0)])
case = Case(buses=[bus], generators=[g])

# Create the market.
mkt = SmartMarket(case)

# Create an agent and place the generator in its environment.
num_actions = 10
env = ParticipantEnvironment(g, mkt)
task = DiscreteTask(env, num_actions)
module = PropensityTable(num_actions)
module.initialize(1.0)
learner = RothErev()
agent = LearningAgent(module, learner)

# Create an experiment to coordinate the agent and its task.
exp = MarketExperiment([task], [agent], mkt)

# Prepare a plotter.
pylab.ion()
pl = MultilinePlotter(autoscale=1.1, xlim=[0, 24], ylim=[0, 1])

x = 0
batch = 5
while x <= 1200:
    exp.doInteractions(batch)

    reward = scipy.mean(agent.history.getSumOverSequences('reward'))
    pl.addData(0, x, reward)
    pl.update()

    agent.learn()
    agent.reset()
    x += batch
