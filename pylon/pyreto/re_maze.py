from pybrain.rl.environments.mazes import Maze
from pybrain.rl.experiments import ContinuousExperiment
from pybrain.rl.agents import EpsilonGreedyAgent
from pybrain.rl import Task

from scipy import array
import sys, time
import pylab

from roth_erev import RothErev, PropensityTable

class MazeTask(Task):
    def getReward(self):
        """ compute and return the current reward (i.e. corresponding to the
            last action performed)
        """
        if self.env.goal == self.env.perseus:
            self.env.reset()
            reward = 1.
        else:
            reward = 0.
        return reward

    def performAction(self, action):
        """ a filtered mapping towards performAction of the underlying
            environment.
        """
        Task.performAction(self, int(action[0]))


    def getObservation(self):
        """ a filtered mapping to getSample of the underlying environment.
        """
        obs = array([self.env.perseus[0] * self.env.mazeTable.shape[0] + \
                     self.env.perseus[1]])
        return obs

# create environment
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
task = MazeTask(env)

actionDomain = {'N': 0, 'S': 1, 'E': 2, 'W': 3}
table = PropensityTable(actionDomain)
#table.initialize(1.0)

# create agent with controller and learner
agent = EpsilonGreedyAgent(table, RothErev())


experiment = ContinuousExperiment(task, agent)


for i in range(100000):
    experiment.doInteractionsAndLearn()
