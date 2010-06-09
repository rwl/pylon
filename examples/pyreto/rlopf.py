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
case.generators[0].p_cost = (0.0, 32.0, 200.0)
case.generators[1].p_cost = (0.0, 2.0, 200.0)
case.generators[2].p_cost = (0.0, 16.0, 200.0)
case.buses[3].p_demand = 100.0
case.buses[4].p_demand = 100.0
case.buses[5].p_demand = 100.0
#plotGenCost(case.generators)

# Assume initial demand is peak demand and save it.
Pd0 = [b.p_demand for b in case.buses if b.type == pylon.PQ]

# Define a 24-hour load profile with hourly values.
p1h = [0.52, 0.54, 0.52, 0.50, 0.52, 0.57, 0.60, 0.71, 0.89, 0.85, 0.88, 0.94,]
#       0.90, 0.88, 0.88, 0.82, 0.80, 0.78, 0.76, 0.68, 0.68, 0.68, 0.65, 0.58]
#p1h = [x + 0.7 * (1.0 - x) for x in p1h]
#p1h = [1.0, 1.0]
nf = len(p1h)

# Create an environment.
env = pyreto.CaseEnvironment(case, p1h)

# Create a task.
task = pyreto.MinimiseCostTask(env)

# Create a controller network.
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
#learner.explorer.sigma = [-2.0] * ng
#learner.explorer.epsilon = 0.01 # default: 0.3
#learner.learningRate = 0.01 # (0.1-0.001, down to 1e-7 for RNNs)

# Alternatively, use blackbox optimisation.
#learner = HillClimber(storeAllEvaluations=True)
##learner = CMAES(storeAllEvaluations=True)
##learner = FEM(storeAllEvaluations=True)
##learner = ExactNES(storeAllEvaluations=True)
##learner = PGPE(storeAllEvaluations=True)
#agent = OptimizationAgent(net, learner)

# print weights at beginning
print "PARAMS:", agent.module.params

# Prepare for plotting.
pylab.figure()#figsize=(16,8))
pylab.ion()
plot = MultilinePlotter(autoscale=1.1, xlim=[0, nf], ylim=[0, 1])

colors = ["black", "black", "orange", "red", "green", "blue"]

f_dc = scipy.io.mmread("../data/fDC.mtx").flatten()
f_ac = scipy.io.mmread("../data/fAC.mtx").flatten()
Pg_dc = scipy.io.mmread("../data/PgDC.mtx").flatten()
Pg_ac = scipy.io.mmread("../data/PgAC.mtx").flatten()
Qg_ac = scipy.io.mmread("../data/QgAC.mtx").flatten()

rday = range(nf)
for i in range(len(case.online_generators)):
    plot.setData(i, rday, numpy.zeros(nf))
plot.setData(3, rday, f_dc[:nf])
plot.setData(4, rday, f_ac[:nf])
plot.setData(5, rday, numpy.zeros(nf)) # reward
#color or c: any matplotlib color
#dash_capstyle: ['butt' | 'round' | 'projecting']
#dash_joinstyle: ['miter' | 'round' | 'bevel']
#dashes: sequence of on/off ink in points
#data: (array xdata, array ydata)
#figure: a matplotlib.figure.Figure instance
#label: any string
#linestyle or ls: [ '-' | '--' | '-.' | ':' | 'steps' | 'None' | ' ' | '' ]
#linewidth or lw: float value in points
#marker: [ '+' | ',' | '.' | '1' | '2' | '3' | '4'
#markeredgecolor or mec: any matplotlib color
#markeredgewidth or mew: float value in points
#markerfacecolor or mfc: any matplotlib color
#markersize or ms: float
#solid_capstyle: ['butt' | 'round' |  'projecting']
#solid_joinstyle: ['miter' | 'round' | 'bevel']
plot.setLineStyle(0, color="red")
plot.setLineStyle(1, color="green")
plot.setLineStyle(2, color="blue")
plot.setLineStyle(3, color="black")
plot.setLineStyle(4, color="gray")
plot.setLineStyle(5, color="orange")
plot.setLineStyle(linewidth=2)
plot.update()

# Create an experiment.
experiment = EpisodicExperiment(task, agent)

weeks = 52
days = 7 # number of samples per gradient estimate
et = ExTools(days, weeks, kind = "learner") #tool for printing and plotting
for week in range(weeks):
    all_rewards = experiment.doEpisodes(number=days)
    #f_n = -1.0 * numpy.array( all_rewards[0][-nf:] )
    #plot.setData(0, rday, f_n)

    tot_reward = numpy.mean(agent.history.getSumOverSequences('reward'))
    print "PARAMS:", agent.module.params

#    print learner._allEvaluations#[-:-1]

    r = -1.0 * numpy.array(all_rewards).reshape(days, nf)
    avg_r = numpy.mean(r, 0)
    plot.setData(5, rday, avg_r)

    for i in range(len(case.online_generators)):
        scale_factor = 10
        plot.setData(i, rday, env._Pg[i, :] * scale_factor)

    agent.learn()
    agent.reset()

    plot.update()

#state, action, reward = agent.learner.dataset.getSequence(
#    agent.learner.dataset.getNumSequences() - 1)
#et.printResults(reward.sum(), runs=1, updates=week)

#pylab.figure()
#pylab.plot(f_dc, "g+-")
#pylab.plot(f_ac, "mx-")
#f_n = numpy.array( all_rewards[0][-len(p1h):] )
#pylab.plot(-1.0 * f_n, "ro-")
#pylab.show()

# Serialize the ReinforcementDataSet.
agent.history.saveToFile("/tmp/ds.pkl", protocol=-1)

pylab.savefig("/tmp/rlopf.png")
