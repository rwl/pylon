__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script runs the first experiment from chapter 5 of Learning to Trade
Power by Richard Lincoln. """

import pyreto.continuous
import pyreto.roth_erev #@UnusedImport

from pyreto.roth_erev import VariantRothErev

from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport

from common import \
    get_case6ww, setup_logging, get_discrete_task_agent, get_zero_task_agent, \
    run_experiment, save_result


setup_logging()

profile = [1.0]
nOffer = 1
nStates = 3


def get_re_experiment(case):
    """ Returns an experiment that uses the Roth-Erev learning method.
    """
    gen = case.generators
    market = pyreto.SmartMarket(case, priceCap=100.0, decommit=True)

    experimentation=0.55
    recency=0.3
    epsilon=100.0
    decay=0.9995

    ##learner1 = pyreto.roth_erev.RothErev(experimentation=0.55, recency=0.3)
    learner1 = VariantRothErev(experimentation, recency)
    learner1.explorer = BoltzmannExplorer(epsilon, decay)
    task1, agent1 = get_discrete_task_agent(
        gen[:1], market, nStates, nOffer, learner1)

    task2, agent2 = get_zero_task_agent(gen[1:2], market, nOffer, profile)

    learner3 = VariantRothErev(experimentation, recency)
    learner3.explorer = BoltzmannExplorer(epsilon, decay)
    task3, agent3 = get_discrete_task_agent(
        gen[:1], market, nStates, nOffer, learner3)

    experiment = pyreto.continuous.MarketExperiment(
        [task1, task2, task3], [agent1, agent2, agent3], market, profile)

    return experiment


def get_q_experiment(case):
    """ Returns an experiment that uses Q-learning.
    """
    gen = case.generators
    market = pyreto.SmartMarket(case, priceCap=100.0, decommit=True)

    learner1 = Q() #QLambda() SARSA(gamma=0.8)
    #learner1.explorer = BoltzmannExplorer()#tau=100, decay=0.95)
    task1, agent1 = get_discrete_task_agent(
        gen[:1], market, nStates, nOffer, (0, 10, 20, 30), profile, learner1)

    experiment = pyreto.continuous.MarketExperiment(
        [task1], [agent1], market, profile)

    return experiment


if __name__ == "__main__":
    case = get_case6ww()

    re_experiment = get_re_experiment(case)
    action, reward = run_experiment(re_experiment, 208, 1)
    save_result(action, "./out/ex5_1_re_action.mtx", "Experiment 5.1 Roth-Erev actions.")
    save_result(reward, "./out/ex5_1_re_reward.mtx", "Experiment 5.1 Roth-Erev rewards.")
