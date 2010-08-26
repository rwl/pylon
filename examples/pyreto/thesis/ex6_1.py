__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script runs the first experiment from chapter 6 of Learning to Trade
Power by Richard Lincoln. """

from time import time

from numpy import zeros, mean, std

import pyreto.continuous
from pyreto import DISCRIMINATIVE, FIRST_PRICE #@UnusedImport

from pyreto.roth_erev import VariantRothErev
from pyreto.util import ManualNormalExplorer

from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.learners import ENAC, Reinforce #@UnusedImport

from common import \
    get_case24_ieee_rts, get_case24_ieee_rts2, get_case24_ieee_rts3, \
    setup_logging, save_results, save_rewards, run_experiment, \
    get_continuous_task_agent, get_full_year, get_neg_one_task_agent, \
    get_discrete_task_agent, get_zero_task_agent, get_pd_min, get_pd_max, \
    pickle_cases

from plot import plot6_1

setup_logging()

decommit = False
auctionType = FIRST_PRICE#DISCRIMINATIVE
profile = get_full_year() / 100.0
cap = 9999.0
nOffer = 1
markups = (0, 15, 30)
withholds = (0, 25, 50)
markupMax = 30.0
withholdMax = 50.0
maxSteps = 24 # hours


#def get_portfolios():
#    """ Returns a tuple of active and passive portfolio indexes.
#    """
#    g1 = range(0, 4)
#    g2 = range(4, 8)
#    g7 = range(8, 11)
#    g13 = range(11, 14)
#    g14 = [14] # sync cond
#    g15 = range(15, 21)
#    g16 = [21]
#    g18 = [22]
#    g21 = [23]
#    g22 = range(24, 30)
#    g23 = range(30, 33)
#
#    portfolios = [g1 + g2 + g7,
#                  g13 + g23,
#                  g15 + g16,
#                  g18 + g21 + g22]
#
#    passive = g14 # sync_cond
#
#    return portfolios, passive
#
#
#def get_portfolios2():
#    """ Returns portfolios with U12 and U20 generators removed.
#    """
#    g1 = range(0, 2)
#    g2 = range(2, 4)
#    g7 = range(4, 7)
#    g13 = range(7, 10)
#    g14 = [10] # sync cond
#    g15 = [11]
#    g16 = [12]
#    g18 = [13]
#    g21 = [14]
#    g22 = range(15, 21)
#    g23 = range(21, 24)
#
#    portfolios = [g1 + g2 + g7,
#                  g13 + g23,
#                  g15 + g16,
#                  g18 + g21 + g22]
#
#    passive = g14 # sync_cond
#
#    return portfolios, passive


def get_portfolios3():
    """ Returns portfolios with U12 and U20 generators removed and generators
    of the same type at the same bus aggregated.
    """
    g1 = [0]
    g2 = [1]
    g7 = [2]
    g13 = [3]
    g14 = [4] # sync cond
    g15 = [5]
    g16 = [6]
    g18 = [7]
    g21 = [8]
    g22 = [9]
    g23 = [10, 11]

    portfolios = [g1 + g15 + g18,
                  g2 + g16 + g21,
                  g13 + g22,
                  g7 + g23]

    passive = g14 # sync_cond

    return portfolios, passive


def get_passive_experiment(case, minor=1):

    locAdj = "dc"

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=auctionType,
                                locationalAdjustment=locAdj)

    experiment = pyreto.continuous.MarketExperiment([], [], market)

    portfolios, sync_cond = get_portfolios3()

    for gidx in portfolios:
        g = [case.generators[i] for i in gidx]

        task, agent = get_zero_task_agent(g, market, nOffer, maxSteps)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    passive = [case.generators[i] for i in sync_cond]
    passive[0].p_min = 0.001 # Avoid invalid offer withholding.
    passive[0].p_max = 0.002
    task, agent = get_zero_task_agent(passive, market, nOffer, maxSteps)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def get_re_experiment(case, minor=1):
    """ Returns an experiment that uses the Roth-Erev learning method.
    """
    locAdj = "ac"
    experimentation = 0.55
    recency = 0.3
    tau = 100.0
    decay = 0.999
    nStates = 1 # stateless RE?

    Pd0 = get_pd_max(case, profile)
    Pd_min = get_pd_min(case, profile)

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=auctionType,
                                locationalAdjustment=locAdj)

    experiment = pyreto.continuous.MarketExperiment([], [], market)

    portfolios, sync_cond = get_portfolios3()

    for gidx in portfolios:
        g = [case.generators[i] for i in gidx]

        learner = VariantRothErev(experimentation, recency)
        learner.explorer = BoltzmannExplorer(tau, decay)

        task, agent = get_discrete_task_agent(g, market, nStates, nOffer,
            markups, withholds, maxSteps, learner, Pd0, Pd_min)

        print "ALL ACTIONS:", len(task.env._allActions)

        experiment.tasks.append(task)
        experiment.agents.append(agent)


    passive = [case.generators[i] for i in sync_cond]
    passive[0].p_min = 0.001 # Avoid invalid offer withholding.
    passive[0].p_max = 0.002
    task, agent = get_zero_task_agent(passive, market, nOffer, maxSteps)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def get_q_experiment(case, minor=1):

    locAdj = "ac"
    nStates = 3
    alpha = 0.2 # Learning rate.
    gamma = 0.99 # Discount factor
    # The closer epsilon gets to 0, the more greedy and less explorative.
    epsilon = 0.9
    decay = 0.999

    Pd0 = get_pd_max(case, profile)
    Pd_min = get_pd_min(case, profile)

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=auctionType,
                                locationalAdjustment=locAdj)

    experiment = pyreto.continuous.MarketExperiment([], [], market)

    portfolios, sync_cond = get_portfolios3()

    for gidx in portfolios:
        g = [case.generators[i] for i in gidx]

        learner = Q(alpha, gamma)
        learner.explorer.epsilon = epsilon
        learner.explorer.decay = decay

        task, agent = get_discrete_task_agent(g, market, nStates, nOffer,
            markups, withholds, maxSteps, learner, Pd0, Pd_min)

        print "ALL ACTIONS:", len(task.env._allActions) * nStates

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    passive = [case.generators[i] for i in sync_cond]
    passive[0].p_min = 0.001 # Avoid invalid offer withholding.
    passive[0].p_max = 0.002
    task, agent = get_zero_task_agent(passive, market, nOffer, maxSteps)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def get_reinforce_experiment(case):

    locAdj = "ac"
    initalSigma = 0.0
    sigmaOffset = -5.0
    decay = 0.995
    learningRate = 0.01

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=auctionType,
                                locationalAdjustment=locAdj)


    experiment = \
        pyreto.continuous.MarketExperiment([], [], market, branchOutages=None)

    portfolios, sync_cond = get_portfolios3()

    for gidx in portfolios:
        g = [case.generators[i] for i in gidx]

        learner = Reinforce()
        learner.learningRate = learningRate

        task, agent = get_continuous_task_agent(g, market, nOffer, markupMax,
                                                withholdMax, maxSteps, learner)

        learner.explorer = ManualNormalExplorer(agent.module.outdim,
                                                initalSigma, decay,
                                                sigmaOffset)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    # Have an agent bid at marginal cost (0.0) for the sync cond.
    passive = [case.generators[i] for i in sync_cond]
    passive[0].p_min = 0.001 # Avoid invalid offer withholding.
    passive[0].p_max = 0.002
    task, agent = get_neg_one_task_agent(passive, market, nOffer, maxSteps)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def get_enac_experiment(case):

    locAdj = "ac"
    initalSigma = 0.0
    sigmaOffset = -5.0
    decay = 0.995
    learningRate = 0.005

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=auctionType,
                                locationalAdjustment=locAdj)

    experiment = \
        pyreto.continuous.MarketExperiment([], [], market, branchOutages=None)

    portfolios, sync_cond = get_portfolios3()

    for gidx in portfolios:
        g = [case.generators[i] for i in gidx]

        learner = ENAC()
        learner.learningRate = learningRate

        task, agent = get_continuous_task_agent(g, market, nOffer, markupMax,
                                                withholdMax, maxSteps, learner)

        learner.explorer = ManualNormalExplorer(agent.module.outdim,
                                                initalSigma, decay,
                                                sigmaOffset)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    # Have an agent bid at marginal cost (0.0) for the sync cond.
    passive = [case.generators[i] for i in sync_cond]
    passive[0].p_min = 0.001 # Avoid invalid offer withholding.
    passive[0].p_max = 0.002
    task, agent = get_neg_one_task_agent(passive, market, nOffer, maxSteps)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def run_years(func, case, roleouts, episodes, in_cloud):

    experiment = func(case)

    dynProfile = profile.reshape((364, maxSteps))
#    maxSteps = dynProfile.shape[1]

    na = len(experiment.agents)
#    ni = roleouts * episodes * maxSteps # no. interactions

#    expt_reward = zeros((na, ni))

    _, reward, epsilon = \
        run_experiment(experiment, roleouts, episodes, in_cloud, dynProfile)

#    expt_reward[expt, :, :] = reward

    experiment = func(case)

    reward_mean = zeros((na, maxSteps))
    reward_std = zeros((na, maxSteps))

    for s in range(maxSteps):
        reward_mean[:, s] = mean(reward[:, s::maxSteps], axis=1)
        reward_std[:, s] = std(reward[:, s::maxSteps], axis=1, ddof=1)

    return reward, (None, None, reward_mean, reward_std, epsilon)


def ex6_1():
    version = "6_1"

    case = get_case24_ieee_rts3()

    in_cloud = False
    years = 1
    roleouts = 364 * years
    episodes = 1 # number of days per learning step

    t0 = time()

#    rewards, results = run_years(get_passive_experiment, case, roleouts,
#                                 episodes, in_cloud)
#    save_results(results, "passive", version)
#    save_rewards(rewards, "passive", version)
    t_passive = time()

#    rewards, results = run_years(get_re_experiment, case, roleouts,
#                                 episodes, in_cloud)
#    save_results(results, "RothErev", version)
#    save_rewards(rewards, "RothErev", version)
    t_re = time()

#    rewards, results = run_years(get_q_experiment, case, roleouts,
#                                 episodes, in_cloud)
#    save_results(results, "Q", version)
#    save_rewards(rewards, "Q", version)
    t_q = time()


    roleouts = 52 * years
    episodes = 7 # number of days per learning step

#    rewards, results = run_years(get_reinforce_experiment, case, roleouts,
#                                 episodes,in_cloud)
#    save_results(results, "REINFORCE", version)
#    save_rewards(rewards, "REINFORCE", version)
    t_reinforce = time()

#    rewards, results = run_years(get_enac_experiment, case, roleouts,
#                                 episodes,in_cloud)
#    save_results(results, "ENAC", version)
#    save_rewards(rewards, "ENAC", version)
    t_enac = time()

    print "Roth-Erev completed in %.2fs." % (t_re - t_passive)
    print "Q-learning completed in %.2fs." % (t_q - t_re)
    print "REINFORCE completed in %.2fs." % (t_reinforce - t_q)
    print "ENAC completed in %.2fs." % (t_enac - t_reinforce)
    print "Experiment 6.1 completed in %.2fs." % (time() - t0)


def main():
#    pickle_cases()
    ex6_1()
    plot6_1()


if __name__ == "__main__":
    main()
