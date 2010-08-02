__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script runs the first experiment from chapter 5 of Learning to Trade
Power by Richard Lincoln. """

import pyreto.continuous
import pyreto.roth_erev #@UnusedImport

from pyreto.roth_erev import VariantRothErev

from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport

from common import \
    get_case6ww, setup_logging, get_discrete_task_agent, get_zero_task_agent


setup_logging()

profile = [1.0]
nOffer = 1
nStates = 3

def get_re_experiment(case):
    """ Returns an experiment that uses the Roth-Erev learning method.
    """
    market = pyreto.SmartMarket(case, priceCap=100.0, decommit=True)

    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    experimentation=0.55
    recency=0.3
    epsilon=100.0
    decay=0.9995

    ##learner1 = pyreto.roth_erev.RothErev(experimentation=0.55, recency=0.3)
    learner1 = VariantRothErev(experimentation, recency)
    learner1.explorer = BoltzmannExplorer(epsilon, decay)
    ta1 = get_discrete_task_agent(case.generators[:1], market, nStates, nOffer, learner1)

    for task, agent in [ta1]:
        experiment.tasks.append(task)
        experiment.agents.append(agent)

    return experiment


def get_q_experiment(case):
    """ Returns an experiment that uses Q-learning.
    """
    market = pyreto.SmartMarket(case, priceCap=100.0, decommit=True)

    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    learner1 = Q() #QLambda() SARSA(gamma=0.8)
    #learner1.explorer = BoltzmannExplorer()#tau=100, decay=0.95)
    ta1 = get_discrete_task_agent(case.generators[:1], market, nStates, nOffer,
                                  (0, 10, 20, 30), profile, learner1)

    for task, agent in [ta1]:
        experiment.tasks.append(task)
        experiment.agents.append(agent)

    return experiment


def run_experiment(experiment, roleouts, samples):
    """ Runs the given experiment and returns the results.
    """
    for roleout in range(roleouts):
        experiment.doEpisodes(samples) # number of samples per learning step

        for agent in experiment.agents:
            agent.learn()
            agent.reset()


if __name__ == "__main__":
    case = get_case6ww()

    re_experiment = get_re_experiment(case)
    run_experiment(re_experiment, 208, 1)
