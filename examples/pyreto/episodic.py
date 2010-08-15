__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use Pyreto to simulate an episodic power
exchange auction market. """

import sys
import logging
import pylab
import scipy

import pyreto.util
import pyreto.continuous

from pylon import Case, OPF

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import ENAC, Reinforce
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.plotting import MultilinePlotter
from pybrain.structure import TanhLayer, LinearLayer #@UnusedImport

logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

# Saved case formats are recognised by file extension.
case = Case.load("../data/case6ww.pkl")

#case.generators[0].p_cost = (0.0, 9.0, 200.0)
#case.generators[1].p_cost = (0.0, 2.0, 200.0)
#case.generators[2].p_cost = (0.0, 5.0, 200.0)

case.generators[0].p_cost = (0.0, 5.0, 200.0)
case.generators[1].p_cost = (0.0, 7.0, 200.0)
case.generators[2].p_cost = (0.0, 2.0, 200.0)

case.generators[0].c_shutdown = 100.0

case.generators[0].p_max = 100.0
case.generators[1].p_max = 70.0
case.generators[2].p_max = 70.0

#pyreto.util.plotGenCost(case.generators)

# Construct a market and specify any desired limits.
market = pyreto.SmartMarket(case, priceCap=100.0, decommit=True)

# Define a 24-hour load profile with hourly values.
#p1h = [0.52, 0.54, 0.52, 0.50, 0.52, 0.57, 0.60, 0.71, 0.89, 0.85, 0.88, 0.94,
#       0.90, 0.88, 0.88, 0.82, 0.80, 0.78, 0.76, 0.68, 0.68, 0.68, 0.65, 0.58]
#p1h = p1h[8:14]
p1h = scipy.array([0.65] * 5)#, 0.95]

# An experiment coordinates interactions between agents and their tasks.
experiment = pyreto.continuous.MarketExperiment([], [], market, p1h)

# A participant may submit any number of offers/bids for each of the
# generators in its portfolio.
numOffbids = 1

# Scale sigma manually?
manual_sigma = True

# Associate each generator in the case with an agent.
for gen in case.generators[:1]:
    # The environment provides market and case sensor values and handles
    # submission of offers/bids to the market.
    env = pyreto.continuous.MarketEnvironment([gen], market, numOffbids)
    # Reward is defined as profit.
    task = pyreto.continuous.ProfitTask(env, maxSteps=len(p1h), maxMarkup=60.0)
    # Build an ANN for policy function approximation.
#    net = buildNetwork(env.outdim, 7, env.indim, bias=True, outputbias=False)
    net = buildNetwork(env.outdim, 2, env.indim,
                       bias=True, outputbias=True,
                       hiddenclass=TanhLayer, outclass=TanhLayer)
    print "NET:", env.outdim, env.indim, net

    # Create an agent and select an episodic learner.
#    learner = ENAC()
    learner = Reinforce()
    learner.gd.rprop = False
    # only relevant for BP
#    learner.learningRate = 0.001 # (0.1-0.001, down to 1e-7 for RNNs, default: 0.1)
    learner.gd.alpha = 0.0001
#    learner.gd.alphadecay = 0.9
#    learner.gd.momentum = 0.9
    # only relevant for RP
#    learner.gd.deltamin = 0.0001

    agent = LearningAgent(net, learner)
    # Name the agent according to its first generator's name.
    agent.name = gen.name

    # Adjust some parameters of the NormalExplorer.
    if manual_sigma:
        sigma = [-5.0] * env.indim
        learner.explorer.sigma = sigma
    # Add the task and agent to the experiment.
    experiment.tasks.append(task)
    experiment.agents.append(agent)

takers = case.generators[1:]
for g in takers:
    env = pyreto.continuous.MarketEnvironment([g], market, numOffbids)
    task = pyreto.continuous.ProfitTask(env, maxSteps=len(p1h))
    agent = pyreto.util.NegOneAgent(env.outdim, env.indim)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

# Prepare for plotting.
pylab.figure()#figsize=(16,8))
pylab.ion()
plot = MultilinePlotter(autoscale=1.1, xlim=[0, len(p1h)], ylim=[0, 1])

# Solve an initial OPF.
OPF(case, market.locationalAdjustment=='dc', opt={"verbose": False}).solve()

weeks = 208 # number of roleouts
days = 7 # number of samples per learning step
for week in range(weeks):
    experiment.doEpisodes(days)

    if manual_sigma:
#        sigma = [sig - abs(sig * 0.05) - 0.1 for sig in sigma]
        sigma = [sig - 1.0 for sig in sigma]
        print "SIGMA:", sigma

    reward = experiment.agents[0].history["reward"]
    plot.addData(0, week, scipy.mean(reward))

    for i, agent in enumerate(experiment.agents):
        agent.learn()
        agent.reset()

#        if manual_sigma and hasattr(agent, "learner"):
#            agent.learner.explorer.sigma = sigma

    print "ALPHA:", experiment.agents[0].learner.gd.alpha
    print "PARAMS:", experiment.agents[0].module.params

    plot.update()

pylab.savefig("/tmp/pyreto.png")
