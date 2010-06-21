__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the discrete Roth-Erev reinforcement
learning algorithms to learn the n-armed bandit task. """

import pylab
import scipy

from pybrain.rl.agents import LearningAgent
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.experiments import Experiment

from pyreto.bandit import BanditEnvironment, BanditTask
from pyreto.roth_erev import RothErev, PropensityTable #@UnusedImport
from pyreto.roth_erev import VariantRothErev #@UnusedImport

payouts = scipy.array([[200.0, 300.0, 100.0],  # Expected value: 210
                       [900.0, 400.0, 600.0],  # Expected value: 510
                       [700.0, 600.0, 550.0],  # Expected value: 595
                       [150.0, 50.0, 1000.0],  # Expected value: 147.5
                       [700.0, 800.0, 900.0]]) # Expected value: 790

distrib = scipy.array([[0.7, 0.2, 0.1],
                       [0.1, 0.6, 0.3],
                       [0.4, 0.2, 0.3],
                       [0.5, 0.45, 0.05],
                       [0.3, 0.5, 0.2]])

env = BanditEnvironment(payouts, distrib)

task = BanditTask(env)

table = PropensityTable(payouts.shape[0])
table.initialize(500.0)

#learner = RothErev(experimentation=0.55, recency=0.3)
learner = VariantRothErev(experimentation=0.65, recency=0.3)
learner.explorer = BoltzmannExplorer(tau=100.0, decay=0.9995)

agent = LearningAgent(table, learner)

experiment = Experiment(task, agent)

epis = int(1e1)
batch = 2
avgRewards = scipy.zeros(epis)
allActions = scipy.zeros(epis * batch)
c = 0
for i in range(epis):
    experiment.doInteractions(batch)
    avgRewards[i] = scipy.mean(agent.history["reward"])
    allActions[c:c + batch] = agent.history["action"].flatten() + 1
    agent.learn()
    agent.reset()

    c += batch

pylab.figure(figsize=(16, 6))
#pylab.plot(avgRewards)
pylab.plot(allActions)
pylab.show()
