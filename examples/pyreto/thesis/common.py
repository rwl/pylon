__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" Functions common to all experiments. """

import os
import sys
import logging

from numpy import zeros, c_
from scipy.io import mmwrite

import pylon

import pyreto.discrete
import pyreto.continuous

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import TanhLayer, LinearLayer #@UnusedImport

def setup_logging():
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler) # rm pybrain
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)


def get_case6ww():
    """ Returns the 6 bus case from Wood & Wollenberg.
    """
    path = os.path.dirname(pylon.__file__)
    path = os.path.join(path, "test", "data")
    path = os.path.join(path, "case6ww", "case6ww.pkl")

    case = pylon.Case.load(path)
    case.generators[0].p_cost = (0.0, 5.0, 200.0)
    case.generators[1].p_cost = (0.0, 6.5, 200.0)
    case.generators[2].p_cost = (0.0, 2.0, 200.0)

    case.generators[0].c_shutdown = 100.0

    #case.generators[0].p_min = 0.0 # TODO: Unit-decommitment.
    #case.generators[1].p_min = 0.0
    ##case.generators[2].p_min = 0.0

    case.generators[0].p_max = 100.0
    case.generators[1].p_max = 70.0
    case.generators[2].p_max = 70.0

    #pyreto.util.plotGenCost(case.generators)

    return case


def get_case24_ieee_rts():
    """ Returns the 24 bus IEEE Reliability Test System.
    """
    path = os.path.dirname(pylon.__file__)
    path = os.path.join(path, "test", "data")
    path = os.path.join(path, "case24_ieee_rts", "case24_ieee_rts.pkl")

    case = pylon.Case.load(path)

    return case


def get_discrete_task_agent(generators, market, nStates, nOffer, markups, profile, learner):
    """ Returns a tuple of task and agent for the given learner.
    """
    env = pyreto.discrete.MarketEnvironment(generators, market,
                                            numStates=nStates, numOffbids=nOffer,
                                            markups=markups)
    task = pyreto.discrete.ProfitTask(env, maxSteps=len(profile))

    nActions = len(env._allActions)
    module = ActionValueTable(numStates=nStates, numActions=nActions)

    agent = LearningAgent(module, learner)

    return task, agent


def get_continuous_task_agent(generators, market, nOffer, maxMarkup, profile, learner):
        env = pyreto.continuous.MarketEnvironment(generators, market, nOffer)

        task = pyreto.continuous.ProfitTask(env, maxSteps=len(profile),
                                            maxMarkup=maxMarkup)

        net = buildNetwork(env.outdim, 2, env.indim,
                           bias=True, outputbias=True,
                           hiddenclass=TanhLayer, outclass=TanhLayer)

        agent = LearningAgent(net, learner)
        agent.name = generators[0].name

        return task, agent


def get_zero_task_agent(generators, market, nOffer, profile):
    """ Returns a task-agent tuple whose action is always zero.
    """
    env = pyreto.discrete.MarketEnvironment(generators, market, nOffer)
    task = pyreto.discrete.ProfitTask(env, maxSteps=len(profile))
    agent = pyreto.util.ZeroAgent(env.outdim, env.indim)
    return task, agent


def run_experiment(experiment, roleouts, samples):
    """ Runs the given experiment and returns the results.
    """
    na = len(experiment.agents)
    all_action = zeros((na, 0))
    all_reward = zeros((na, 0))

    for roleout in range(roleouts):
        experiment.doEpisodes(samples) # number of samples per learning step

        epi_action = zeros((0, samples))
        epi_reward = zeros((0, samples))

        for agent in experiment.agents:
            action = agent.history["action"]
            reward = agent.history["reward"]

            epi_action = c_[epi_action.T, action].T
            epi_reward = c_[epi_reward.T, reward].T

            agent.learn()
            agent.reset()

        all_action = c_[all_action, epi_action]
        all_reward = c_[all_reward, epi_reward]

    return all_action, all_reward


def save_result(result, path, comment=""):
    """ Saves the given results to the path in MatrixMarket format.
    """
    mmwrite(path, result, comment)
