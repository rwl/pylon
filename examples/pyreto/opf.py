__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how optimise power flow with Pyreto. """

import sys
import logging
import numpy
import pylon
import pyreto

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import ENAC
from pybrain.rl.experiments import EpisodicExperiment
from pybrain.tools.shortcuts import buildNetwork

logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler) # rm pybrain
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

case = pylon.Case.load("../data/case6ww.pkl")

# Assume initial demand is peak demand and save it.
Pd0 = [b.p_demand for b in case.buses if b.type == pylon.PQ]

# Define a 24-hour load profile with hourly values.
p1h = [0.52, 0.54, 0.52, 0.50, 0.52, 0.57, 0.60, 0.71, 0.89, 0.85, 0.88, 0.94,
       0.90, 0.88, 0.88, 0.82, 0.80, 0.78, 0.76, 0.68, 0.68, 0.68, 0.65, 0.58]

# Create an environment.
env = pyreto.CaseEnvironment(case, p1h)

# Create a task.
task = pyreto.MinimiseCostTask(env)

# Create a controller network.
nb = len([bus for bus in case.buses if bus.type == pylon.PQ])
ng = len([g for g in case.online_generators if g.bus.type != pylon.REFERENCE])
net = buildNetwork(nb, ng, bias=False)

# Create an agent and select an episodic learner.
agent = LearningAgent(net, ENAC())

# Create an experiment.
experiment = EpisodicExperiment(task, agent)
all_rewards = experiment.doEpisodes(number=2)
print "Min: %.3f" % -max(max(all_rewards))

# Determine minimum cost using PIPS.
min_cost = numpy.zeros(len(p1h))
for i, fraction in enumerate(p1h):
    for j, bus in enumerate([b for b in case.buses if b.type == pylon.PQ]):
        bus.p_demand = p1h[i] * Pd0[j]
    s = pylon.OPF(case).solve()
    min_cost[i] = s["f"]
