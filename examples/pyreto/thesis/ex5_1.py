__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script runs the first experiment from chapter 5 of Learning to Trade
Power by Richard Lincoln. """

from numpy import zeros, mean, std

from pyreto import DISCRIMINATIVE

import pyreto.continuous
import pyreto.roth_erev #@UnusedImport

from pyreto.roth_erev import VariantRothErev
from pyreto.util import ManualNormalExplorer

from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.learners import ENAC, Reinforce #@UnusedImport

from common import \
    get_case6ww, setup_logging, get_discrete_task_agent, get_zero_task_agent, \
    run_experiment, save_results, get_continuous_task_agent, \
    get_neg_one_task_agent

from plot import plot5_1


setup_logging()

decommit = False
cap = 100.0
profile = [1.0]
nOffer = 1
nStates = 1
manual_sigma = True # Scale sigma manually?

def get_re_experiment(case):
    """ Returns an experiment that uses the Roth-Erev learning method.
    """
    gen = case.generators

    experimentation = 0.55
    recency = 0.3
    tau = 100.0
    decay = 0.98#9995
    markups = (0, 10, 20, 30)

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
#                                auctionType=DISCRIMINATIVE
                                )

    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    for g in gen[0:2]:
        #learner = RothErev(experimentation, recency)
        learner = VariantRothErev(experimentation, recency)
        learner.explorer = BoltzmannExplorer(tau, decay)

        task, agent = get_discrete_task_agent(
            [g], market, nStates, nOffer, markups, profile, learner)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    task1, agent1 = get_zero_task_agent(gen[2:3], market, nOffer, profile)
    experiment.tasks.append(task1)
    experiment.agents.append(agent1)

    return experiment


def get_q_experiment(case):
    """ Returns an experiment that uses Q-learning.
    """
    gen = case.generators

    alpha = 0.3 # Learning rate.
    gamma = 0.99 # Discount factor
    # The closer epsilon gets to 0, the more greedy and less explorative.
    epsilon = 0.5
    decay = 0.995
    tau = 150.0 # Boltzmann temperature.
    markups = (0, 10, 20, 30)
    qlambda = 0.9

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
#                                auctionType=DISCRIMINATIVE
                                )

    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    for g in gen[0:2]:
        learner = Q(alpha, gamma)
    #    learner = QLambda(alpha, gamma, qlambda)
    #    learner = SARSA(alpha, gamma)

        learner.explorer.epsilon = epsilon
        learner.explorer.decay = decay
#        learner.explorer = BoltzmannExplorer(tau, decay)

        task, agent = get_discrete_task_agent(
            [g], market, nStates, nOffer, markups, profile, learner)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    # Passive agent.
    task, agent = get_zero_task_agent(gen[2:3], market, nOffer, profile)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def get_reinforce_experiment(case):
    gen = case.generators

    markupMax = 30.0
    initalSigma = 100.0
    decay = 0.995

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
#                                auctionType=DISCRIMINATIVE
                                )
    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    for g in gen[0:2]:
        learner = Reinforce()
        learner.gd.rprop = False
        # only relevant for BP
        learner.learningRate = 0.001 # (0.1-0.001, down to 1e-7 for RNNs, default: 0.1)
        learner.gd.alpha = 0.0001
        learner.gd.alphadecay = 0.9
        learner.gd.momentum = 0.9
        # only relevant for RP
        learner.gd.deltamin = 0.0001

        task, agent = get_continuous_task_agent(
            [g], market, nOffer, markupMax, profile, learner)

        learner.explorer = ManualNormalExplorer(agent.module.outdim,
                                                initalSigma, decay)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    # Passive agent.
    task, agent = get_neg_one_task_agent(gen[2:3], market, nOffer, profile)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def get_enac_experiment(case):
    gen = case.generators

    markupMax = 30.0
    initalSigma = 100.0
    decay = 0.995

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
#                                auctionType=DISCRIMINATIVE
                                )
    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    for g in gen[0:2]:
        learner = ENAC()
#        learner = Reinforce()
#        learner.gd.rprop = False
        # only relevant for BP
    #    learner.learningRate = 0.001 # (0.1-0.001, down to 1e-7 for RNNs, default: 0.1)
#        learner.gd.alpha = 0.0001
    #    learner.gd.alphadecay = 0.9
    #    learner.gd.momentum = 0.9
        # only relevant for RP
    #    learner.gd.deltamin = 0.0001


        task, agent = get_continuous_task_agent(
            [g], market, nOffer, markupMax, profile, learner)

        learner.explorer = ManualNormalExplorer(agent.module.outdim,
                                                initalSigma, decay)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    # Passive agent.
    task, agent = get_neg_one_task_agent(gen[2:3], market, nOffer, profile)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def run_experiments(expts, func, case, roleouts, in_cloud):
    samples = len(profile)

    experiment = func(case)
    na = len(experiment.agents)

    expt_action = zeros((expts, na, roleouts * samples))
    expt_reward = zeros((expts, na, roleouts * samples))

    for expt in range(expts):
        action, reward, epsilon = run_experiment(
            experiment, roleouts, samples, in_cloud)

        expt_action[expt, :, :] = action
        expt_reward[expt, :, :] = reward

        experiment = func(case)

    expt_action_mean = mean(expt_action, axis=0)
    expt_action_std = std(expt_action, axis=0, ddof=1)

    expt_reward_mean = mean(expt_reward, axis=0)
    expt_reward_std = std(expt_reward, axis=0, ddof=1)

    return expt_action_mean, expt_action_std, \
           expt_reward_mean, expt_reward_std, epsilon


def main():
    case = get_case6ww()

    expts = 1
    roleouts =150
    in_cloud = False

    results = run_experiments(expts, get_re_experiment, case, roleouts,
                              in_cloud)
    save_results(results, "RothErev")


#    results = run_experiments(expts, get_q_experiment, case, roleouts,
#                              in_cloud)
#    save_results(results, "Q")
#
#
#    results = run_experiments(expts, get_reinforce_experiment, case, roleouts,
#                              in_cloud)
#    save_results(results, "REINFORCE")
#
#
#    results = run_experiments(expts, get_enac_experiment, case, roleouts,
#                              in_cloud)
#    save_results(results, "ENAC")


if __name__ == "__main__":
    main()
    plot5_1()
