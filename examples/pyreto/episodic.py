__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use Pylon to simulate an episodic power
exchange auction market. """

import sys
import logging
import pylab
import scipy

from pylon import Case, OPF
import pyreto

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import ENAC
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.plotting import MultilinePlotter

logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

# Saved case formats are recognised by file extension.
case = Case.load("data/auction_case.pickle")

# Construct a market and specify any desired limits.
market = pyreto.SmartMarket(case, price_cap=100.0)

# Define a 24-hour load profile with hourly values.
p1h = [0.52, 0.54, 0.52, 0.50, 0.52, 0.57, 0.60, 0.71, 0.89, 0.85, 0.88, 0.94,
       0.90, 0.88, 0.88, 0.82, 0.80, 0.78, 0.76, 0.68, 0.68, 0.68, 0.65, 0.58]

# An experiment coordinates interactions between agents and their tasks.
experiment = pyreto.EpisodicMarketExperiment([], [], market, p1h)

# Associate each generator in the case with an agent.
for gen in case.generators:
    # The environment provides market and case sensor values and handles
    # submission of offers/bids to the market.
    env = pyreto.ContinuousMarketEnvironment(gen, market, n_offbids=2)
    # Reward is defined as profit.
    task = pyreto.EpisodicProfitTask(env, maxsteps=len(p1h))
    # Build an ANN for policy function approximation.
    net = buildNetwork(env.outdim, int(env.outdim*1.2), env.indim, bias=False)
    # Create an agent and select an episodic learner.
    agent = LearningAgent(net, ENAC())
    # Name the agent according to its generator.
    agent.name = gen.name
    # Add the task and agent to the experiment.
    experiment.tasks.append(task)
    experiment.agents.append(agent)

# Prepare for plotting.
pylab.figure(figsize=(16,8))
pylab.ion()
plot = MultilinePlotter(autoscale=1.1, xlim=[0, len(p1h)], ylim=[0, 1])

# Solve an initial OPF.
OPF(case, market.loc_adjust=='dc').solve()

days = 7 # number of samples per learning step
weeks = 52 / days # number of roleouts

# Do the experiment.
for week in range(weeks):
    experiment.doEpisodes(days)
    for i, agent in enumerate(experiment.agents):
        state, action, reward = \
            agent.history.getSequence(agent.history.getNumSequences() - 1)
        plot.addData(i, week, scipy.mean(reward))
    plot.update()
