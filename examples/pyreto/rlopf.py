__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how optimise power flow with Pyreto. """

import sys
import logging
import numpy
import scipy.io
import pylab
import pylon
import pyreto

from pyreto.tools import plotGenCost

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import ENAC, Reinforce
from pybrain.rl.experiments import EpisodicExperiment
from pybrain.rl.agents import OptimizationAgent
from pybrain.optimization import HillClimber, CMAES, ExactNES, PGPE, FEM
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.plotting import MultilinePlotter
from pybrain.tools.example_tools import ExTools

logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler) # rm pybrain
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

case = pylon.Case.load("../data/case6ww.pkl")
case.generators[0].p_cost = (0.0, 16.0, 200.0)
case.generators[1].p_cost = (0.0, 2.0, 200.0)
case.generators[2].p_cost = (0.0, 32.0, 200.0)
case.buses[3].p_demand = 120.0
case.buses[4].p_demand = 120.0
case.buses[5].p_demand = 120.0
#plotGenCost(case.generators)

# Assume initial demand is peak demand (for sensor limits) and save it.
Pd0 = [b.p_demand for b in case.buses if b.type == pylon.PQ]

# Define a 24-hour load profile with hourly values.
p1h = [0.52, 0.54, 0.52, 0.50, 0.52, 0.57, 0.60, 0.71, 0.89, 0.85, 0.88, 0.94,
       0.90, 0.88, 0.88, 0.82, 0.80, 0.78, 0.76, 0.68, 0.68, 0.68, 0.65, 0.58]
#p1h = p1h[6:-6]
p1h = p1h[:12]
nf = len(p1h)

# Create a case environment specifying the load profile.
env = pyreto.CaseEnvironment(case, p1h)

# Create an episodic cost minimisation task.
task = pyreto.MinimiseCostTask(env)

# Create a network for approximating the agent's policy function that maps
# system demand to generator set-points..
nb = len([bus for bus in case.buses if bus.type == pylon.PQ])
ng = len([g for g in case.online_generators if g.bus.type != pylon.REFERENCE])
net = buildNetwork(nb, ng, bias=False)

# Create an agent and select an episodic learner.
#learner = Reinforce()
learner = ENAC()
#learner.gd.rprop = True
## only relevant for RP
#learner.gd.deltamin = 0.0001
##agent.learner.gd.deltanull = 0.05
## only relevant for BP
#learner.gd.alpha = 0.01
#learner.gd.momentum = 0.9

agent = LearningAgent(net, learner)

# Adjust some parameters of the NormalExplorer.
sigma = [50.0] * ng
learner.explorer.sigma = sigma
#learner.explorer.epsilon = 0.01 # default: 0.3
#learner.learningRate = 0.01 # (0.1-0.001, down to 1e-7 for RNNs)

# Alternatively, use blackbox optimisation.
#learner = HillClimber(storeAllEvaluations=True)
##learner = CMAES(storeAllEvaluations=True)
##learner = FEM(storeAllEvaluations=True)
##learner = ExactNES(storeAllEvaluations=True)
##learner = PGPE(storeAllEvaluations=True)
#agent = OptimizationAgent(net, learner)

# Prepare for plotting.
pylab.figure()#figsize=(16,8))
pylab.ion()
plot = MultilinePlotter(autoscale=1.1, xlim=[0, nf], ylim=[0, 1])

# Read ideal system cost and set-point values determined using OPF.
f_dc = scipy.io.mmread("../data/fDC.mtx").flatten()
f_ac = scipy.io.mmread("../data/fAC.mtx").flatten()
Pg_dc = scipy.io.mmread("../data/PgDC.mtx")
Pg_ac = scipy.io.mmread("../data/PgAC.mtx")
Qg_ac = scipy.io.mmread("../data/QgAC.mtx")

rday = range(nf)
for i in range(len(case.online_generators)):
    plot.setData(i, rday, numpy.zeros(nf))
plot.setData(3, rday, f_dc[:nf])
plot.setData(4, rday, f_ac[:nf])
plot.setData(5, rday, numpy.zeros(nf)) # reward
#plot.setData(6, rday, Pg_ac[:nf] * 10)

plot.setLineStyle(0, color="red")
plot.setLineStyle(1, color="green")
plot.setLineStyle(2, color="blue")
plot.setLineStyle(3, color="black")
plot.setLineStyle(4, color="gray")
plot.setLineStyle(5, color="orange")
#plot.setLineStyle(6, color="black")
plot.setLineStyle(linewidth=2)
plot.update()

# Give the agent its task in an experiment.
#experiment = EpisodicExperiment(task, agent)
experiment = pyreto.rlopf.OPFExperiment(task, agent)

weeks = 52 * 2
days = 5 # number of samples per gradient estimate
for week in range(weeks):
    all_rewards = experiment.doEpisodes(number=days)
    tot_reward = numpy.mean(agent.history.getSumOverSequences('reward'))

#    print learner._allEvaluations#[-:-1]

    # Plot the reward at each period averaged over the week.
    r = -1.0 * numpy.array(all_rewards).reshape(days, nf)
    avg_r = numpy.mean(r, 0)
    plot.setData(5, rday, avg_r)

    # Plot the set-point of each generator on the last day of the week.
    # FIXME: Plot the set-points averaged over the week.
    for i in range(len(case.online_generators)):
        scale_factor = 10
#        plot.setData(i, rday, env._Pg[i, :] * scale_factor)
        plot.setData(i, rday, experiment.Pg[i, :] * scale_factor)

    agent.learn()
    agent.reset()

    # Scale sigma manually.
    sigma = [(sig * 0.95) - 0.05 for sig in sigma]
    learner.explorer.sigma = sigma

    plot.update()

pylab.savefig("/tmp/rlopf.png")
