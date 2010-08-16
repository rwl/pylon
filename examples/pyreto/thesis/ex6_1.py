__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script runs the first experiment from chapter 6 of Learning to Trade
Power by Richard Lincoln. """

from numpy import zeros, mean, std

import pyreto.continuous
from pyreto import DISCRIMINATIVE, FIRST_PRICE #@UnusedImport

from pyreto.roth_erev import VariantRothErev
from pyreto.util import ManualNormalExplorer

from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.learners import ENAC, Reinforce #@UnusedImport

from common import \
    get_case24_ieee_rts, setup_logging, save_results, run_experiment, \
    get_continuous_task_agent, get_full_year, get_neg_one_task_agent, \
    get_discrete_task_agent, get_zero_task_agent, get_pd_min, get_pd_max

setup_logging()

locAdj = "dc"#"dc"
decommit = False
auctionType = FIRST_PRICE#DISCRIMINATIVE
profile = get_full_year() / 100.0
cap = 9999.0
nOffer = 1
nStates = 10
markups = (0, 15, 30)
markupMax = 30.0
maxSteps = 24 # hours


def get_portfolios():
    """ Returns a tuple of active and passive portfolio indexes.
    """
    g1 = range(0, 4)
    g2 = range(4, 8)
    g7 = range(8, 11)
    g13 = range(11, 14)
    g14 = [14] # sync cond
    g15 = range(15, 21)
    g16 = [21]
    g18 = [22]
    g21 = [23]
    g22 = range(24, 30)
    g23 = range(30, 33)

    portfolios = [g1 + g2 + g7,
                  g13 + g23,
                  g15 + g16,
                  g18 + g21 + g22]

    passive = g14 # sync_cond

    return portfolios, passive


def get_re_experiment(case, minor=1):
    """ Returns an experiment that uses the Roth-Erev learning method.
    """
    experimentation = 0.55
    recency = 0.3
    tau = 100.0
    decay = 0.98#9995
#    nStates = 1 # stateless RE?

    Pd0 = get_pd_max(case, profile)
    Pd_min = get_pd_min(case, profile)

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=auctionType)

    experiment = pyreto.continuous.MarketExperiment([], [], market)

    portfolios, sync_cond = get_portfolios()

    for gidx in portfolios:
        g = [case.generators[i] for i in gidx]

        learner = VariantRothErev(experimentation, recency)
        learner.explorer = BoltzmannExplorer(tau, decay)

        task, agent = get_discrete_task_agent(
            g, market, nStates, nOffer, markups, maxSteps, learner, Pd0,Pd_min)

        experiment.tasks.append(task)
        experiment.agents.append(agent)


    passive = [case.generators[i] for i in sync_cond]
    passive[0].p_min = 0.001 # Avoid invalid offer withholding.
    passive[0].p_max = 0.002
    task, agent = get_zero_task_agent(passive, market, nOffer, maxSteps)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def get_enac_experiment(case):

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                locationalAdjustment=locAdj)

    initalSigma = 0.0
    sigmaOffset = -4.0
    decay = 0.995
    learningRate = 0.001

    experiment = \
        pyreto.continuous.MarketExperiment([], [], market, branchOutages=None)

    portfolios, sync_cond = get_portfolios()

    for gidx in portfolios:
        g = [case.generators[i] for i in gidx]

        learner = ENAC()
        learner.learningRate = learningRate

        task, agent = get_continuous_task_agent(
            g, market, nOffer, markupMax, maxSteps, learner)

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


def run_years(func, case, years, roleouts, episodes, in_cloud):

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

    return (None, None, reward_mean, reward_std, epsilon)


def ex6_1():
    version = "6_1"

    case = get_case24_ieee_rts()

    in_cloud = False
    years = 1
    roleouts = 1#364 * years #52 * years
    episodes = 2#7 # number of samples per learning step

    results = \
        run_years(get_re_experiment, case, years, roleouts, episodes, in_cloud)
    save_results(results, "Stateful Roth-Erev", version)

#    results = \
#        run_years(get_enac_experiment, case, years, roleouts,episodes,in_cloud)
#    save_results(results, "ENAC", version)


def main():
    ex6_1()


if __name__ == "__main__":
    main()
