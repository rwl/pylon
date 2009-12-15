__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the discrete Temporal Difference
Reinforcement Learning algorithms (SARSA, Q, Q(lambda)) in a partially
observable MDP energy market task. """

import pylab

from pylon import Case, Bus, Generator

from pylon.pyreto import \
    MarketExperiment, ParticipantEnvironment, SmartMarket, DiscreteTask

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased import ActionValueTable#, ActionValueNetwork
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport

# Define a case with two generators of differing capacity and a fixed load.
g1 = Generator(name="G1", p_max=60.0, p_min=0.0)
g2 = Generator(name="G2", p_max=100.0, p_min=0.0)
bus1 = Bus(name="Bus1", p_demand=80.0, generators=[g1, g2])
case = Case(name="1Bus", buses=[bus1])

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
learner2 = SARSA() #Q() QLambda()
#learner2.explorer = BoltzmannExplorer() # default is e-greedy.
agent2 = LearningAgent(module2, learner2)

exp = MarketExperiment([task1, task2], [agent1, agent2], mkt)

# Prepare for plotting.
pylab.ion()
#fig = pylab.figure(1)
#axis1 = fig.add_subplot(2, 1, 1)
#line1 = axis1.plot([0.0], "mx-")[0]
#axis2 = fig.add_subplot(2, 1, 2)
#line2 = axis2.plot([0.0], "ro-")[0]
#pylab.draw()

# Execute interactions with the enironment in batch mode.
for _ in range(1000):
    exp.doInteractions(5)
    agent1.learn()
    agent1.reset()
    agent2.learn()
    agent2.reset()

    # Plot the progress of the agents.
    pylab.clf()
    pylab.plot(agent1.module.params, "mx-")
    pylab.plot(agent2.module.params, "ro-")
#    line1.set_ydata(agent1.module.params)
#    line2.set_ydata(agent2.module.params)
    pylab.draw()
