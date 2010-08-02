__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" Functions common to all experiments. """

import os
import sys
import logging

import pylon

import pyreto.discrete

from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners.valuebased import ActionValueTable

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


def get_zero_task_agent(generators, market, nOffer, profile):
    """ Returns a task-agent tuple whose action is always zero.
    """
    env = pyreto.discrete.MarketEnvironment(generators, market, nOffer)
    task = pyreto.discrete.ProfitTask(env, maxSteps=len(profile))
    agent = pyreto.util.ZeroAgent(env.outdim, env.indim)
    return task, agent
