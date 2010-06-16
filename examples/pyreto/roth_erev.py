__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This example demonstrates how to use the discrete Roth-Erev reinforcement
learning algorithms. """

from scipy import array, flipud
import pylab

from pybrain.rl.environments.mazes import Maze, MDPMazeTask
from pybrain.rl.agents import LearningAgent
from pybrain.rl.experiments import Experiment

from pyreto import RothErev, PropensityTable # GNU GPL'd


# create the maze with walls (1)
envmatrix = array([[1, 1, 1, 1, 1, 1, 1, 1, 1],
                   [1, 0, 0, 1, 0, 0, 0, 0, 1],
                   [1, 0, 0, 1, 0, 0, 1, 0, 1],
                   [1, 0, 0, 1, 0, 0, 1, 0, 1],
                   [1, 0, 0, 1, 0, 1, 1, 0, 1],
                   [1, 0, 0, 0, 0, 0, 1, 0, 1],
                   [1, 1, 1, 1, 1, 1, 1, 0, 1],
                   [1, 0, 0, 0, 0, 0, 0, 0, 1],
                   [1, 1, 1, 1, 1, 1, 1, 1, 1]])

env = Maze(envmatrix, (7, 7))

# create task
task = MDPMazeTask(env)

# create value table and initialize with ones
table = PropensityTable(4)
table.initialize(1.0)

# create agent with controller and learner - use SARSA(), Q() or QLambda() here
learner = RothErev()

# create agent
agent = LearningAgent(table, learner)

# create experiment
experiment = Experiment(task, agent)

# prepare plotting
pylab.gray()
pylab.ion()

for i in range(1000):

    # interact with the environment (here in batch mode)
    experiment.doInteractions(100)
    agent.learn()
    agent.reset()

    # and draw the table
    pylab.pcolor(flipud(table.params.reshape(81,4).max(1).reshape(9,9)))
    pylab.draw()
