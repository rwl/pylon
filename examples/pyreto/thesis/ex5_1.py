__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script runs the first experiment from chapter 5 of Learning to Trade
Power by Richard Lincoln. """

from numpy import zeros, mean, std, c_, vectorize

from pyreto import DISCRIMINATIVE

import pyreto.continuous
import pyreto.roth_erev #@UnusedImport

from pyreto.roth_erev import VariantRothErev
from pyreto.util import ManualNormalExplorer

from pybrain.rl.learners.directsearch.directsearch import DirectSearchLearner
from pybrain.rl.learners.valuebased.valuebased import ValueBasedLearner

from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.learners import ENAC, Reinforce #@UnusedImport

from common import \
    get_case6ww, get_case6ww2, setup_logging, get_discrete_task_agent, \
    get_zero_task_agent, save_results, \
    get_continuous_task_agent, get_neg_one_task_agent

from plot import plot5_1


setup_logging()

decommit = False
cap = 100.0
#profile = [1.0, 1.0]
nOffer = 1
nStates = 1


def get_re_experiment(case, minor=1):
    """ Returns an experiment that uses the Roth-Erev learning method.
    """
    gen = case.generators

    profile = [1.0]
    experimentation = 0.55
    recency = 0.3
    tau = 100.0
    decay = 0.98#9995
    markups = (0, 10, 20, 30)

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=DISCRIMINATIVE
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


def get_q_experiment(case, minor=1):
    """ Returns an experiment that uses Q-learning.
    """
    gen = case.generators

    profile = [1.0]
    alpha = 0.3 # Learning rate.
    gamma = 0.99 # Discount factor
    # The closer epsilon gets to 0, the more greedy and less explorative.
    epsilon = 0.9
    decay = 0.97
    tau = 150.0 # Boltzmann temperature.
    markups = (0, 10, 20, 30)
    qlambda = 0.9

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=DISCRIMINATIVE
                                )

    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    for g in gen[0:2]:
        learner = Q(alpha, gamma)
    #    learner = QLambda(alpha, gamma, qlambda)
    #    learner = SARSA(alpha, gamma)

#        learner.explorer.epsilon = epsilon
#        learner.explorer.decay = decay
        learner.explorer = BoltzmannExplorer(tau, decay)

        task, agent = get_discrete_task_agent(
            [g], market, nStates, nOffer, markups, profile, learner)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    # Passive agent.
    task, agent = get_zero_task_agent(gen[2:3], market, nOffer, profile)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def get_reinforce_experiment(case, minor=1):
    gen = case.generators

    markupMax = 30.0
    profile = [1.0, 1.0]
    initalSigma = 0.0
#    decay = 0.95
#    learningRate = 0.0005#005 # (0.1-0.001, down to 1e-7 for RNNs, default: 0.1)
    sigmaOffset = -5.0

    if minor == 1:
        decay = 0.98#75#95
        learningRate = 0.01 # (0.1-0.001, down to 1e-7 for RNNs, default: 0.1)
    elif minor == 2:
        decay = 0.985
        learningRate = 0.0005
    else:
        raise ValueError

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=DISCRIMINATIVE
                                )
    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    for g in gen[0:2]:
        learner = Reinforce()
#        learner.gd.rprop = False
        # only relevant for BP
        learner.learningRate = learningRate
#        learner.gd.alpha = 0.0001
#        learner.gd.alphadecay = 0.9
#        learner.gd.momentum = 0.9
        # only relevant for RP
#        learner.gd.deltamin = 0.0001

        task, agent = get_continuous_task_agent(
            [g], market, nOffer, markupMax, profile, learner)

        learner.explorer = ManualNormalExplorer(agent.module.outdim,
                                                initalSigma, decay,
                                                sigmaOffset)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    # Passive agent.
    task, agent = get_neg_one_task_agent(gen[2:3], market, nOffer, profile)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def get_enac_experiment(case, minor=1):
    gen = case.generators

    markupMax = 30.0
    profile = [1.0, 1.0]
    initalSigma = 0.0
    sigmaOffset = -4.0

    if minor == 1:
        decay = 0.995
        learningRate = 0.001 # (0.1-0.001, down to 1e-7 for RNNs, default: 0.1)
    elif minor == 2:
        decay = 0.985
        learningRate = 0.0005
    else:
        raise ValueError

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=DISCRIMINATIVE
                                )
    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    for g in gen[0:2]:
        learner = ENAC()
#        learner = Reinforce()
#        learner.gd.rprop = False
        # only relevant for BP
        learner.learningRate = learningRate
#        learner.gd.alpha = 0.0001
    #    learner.gd.alphadecay = 0.9
    #    learner.gd.momentum = 0.9
        # only relevant for RP
    #    learner.gd.deltamin = 0.0001


        task, agent = get_continuous_task_agent(
            [g], market, nOffer, markupMax, profile, learner)

        learner.explorer = ManualNormalExplorer(agent.module.outdim,
                                                initalSigma, decay,
                                                sigmaOffset)

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    # Passive agent.
    task, agent = get_neg_one_task_agent(gen[2:3], market, nOffer, profile)
    experiment.tasks.append(task)
    experiment.agents.append(agent)

    return experiment


def run_experiment(experiment, roleouts, samples, in_cloud=False):
    """ Runs the given experiment and returns the results.
    """
    def run():
        na = len(experiment.agents)
        ni = roleouts * samples * len(experiment.profile)

        all_action = zeros((na, 0))
        all_reward = zeros((na, 0))
        epsilon = zeros((na, ni)) # exploration rate

        # Converts to action vector in percentage markup values.
        vmarkup = vectorize(get_markup)

        for roleout in range(roleouts):
            experiment.doEpisodes(samples) # number of samples per learning step

            nei = samples * len(experiment.profile) # num interactions per role
            epi_action = zeros((0, nei))
            epi_reward = zeros((0, nei))

            for i, (task, agent) in \
            enumerate(zip(experiment.tasks, experiment.agents)):
                action = agent.history["action"]
                reward = agent.history["reward"]

                for j in range(nei):
                    if isinstance(agent.learner, DirectSearchLearner):
                        action[j, :] = task.denormalize(action[j, :])
                        k = nei * roleout
                        epsilon[i, k:k + nei] = agent.learner.explorer.sigma
                    elif isinstance(agent.learner, ValueBasedLearner):
                        action[j, :] = vmarkup(action[j, :], task)
                        k = nei * roleout
                        epsilon[i, k:k + nei] = agent.learner.explorer.epsilon
                    else:
                        action = vmarkup(action, task)

#                print "EIP", epsilon
#                print action.flatten().shape

                epi_action = c_[epi_action.T, action.flatten()].T
                epi_reward = c_[epi_reward.T, reward.flatten()].T

                agent.learn()
                agent.reset()

                if hasattr(agent, "module"):
                    print "PARAMS:", agent.module.params

            all_action = c_[all_action, epi_action]
            all_reward = c_[all_reward, epi_reward]

        return all_action, all_reward, epsilon

    if in_cloud:
        import cloud
        job_id = cloud.call(run, _high_cpu=False)
        result = cloud.result(job_id)
        all_action, all_reward, epsilon = result
    else:
        all_action, all_reward, epsilon = run()

    return all_action, all_reward, epsilon


def get_markup(a, task):
    i = int(a)
    m = task.env._allActions[i]
    return m[0]


def run_experiments(expts, func, case, roleouts, in_cloud, minor=1):

    experiment = func(case, minor)

    na = len(experiment.agents)
    samples = 3
    ni = roleouts * samples * len(experiment.profile) # no. interactions

    expt_action = zeros((expts, na, ni))
    expt_reward = zeros((expts, na, ni))

    for expt in range(expts):
        action, reward, epsilon = \
            run_experiment(experiment, roleouts, samples, in_cloud)

        expt_action[expt, :, :] = action
        expt_reward[expt, :, :] = reward

        experiment = func(case)

    expt_action_mean = mean(expt_action, axis=0)
    expt_action_std = std(expt_action, axis=0, ddof=1)

    expt_reward_mean = mean(expt_reward, axis=0)
    expt_reward_std = std(expt_reward, axis=0, ddof=1)

    return expt_action_mean, expt_action_std, \
           expt_reward_mean, expt_reward_std, epsilon


def ex5_1():
    minor = 1
    case = get_case6ww()

    expts = 1
    roleouts = 20
    in_cloud = False

#    results = run_experiments(expts, get_re_experiment, case, roleouts,
#                              in_cloud, minor)
#    save_results(results, "RothErev")
#
#
#    results = run_experiments(expts, get_q_experiment, case, roleouts,
#                              in_cloud, minor)
#    save_results(results, "Q")
#
#    results = run_experiments(expts, get_reinforce_experiment, case, roleouts,
#                              in_cloud, minor)
#    save_results(results, "REINFORCE")
#
#
    results = run_experiments(expts, get_enac_experiment, case, roleouts,
                              in_cloud, minor)
    save_results(results, "ENAC")


def ex5_2():
    minor = 2

    case = get_case6ww2()

    expts = 10
    roleouts = 300
    in_cloud = False

    results = run_experiments(expts, get_re_experiment, case, roleouts,
                              in_cloud, minor)
    save_results(results, "RothErev", minor)


    results = run_experiments(expts, get_q_experiment, case, roleouts,
                              in_cloud, minor)
    save_results(results, "Q", minor)


    results = run_experiments(expts, get_reinforce_experiment, case, roleouts,
                              in_cloud, minor)
    save_results(results, "REINFORCE", minor)


    results = run_experiments(expts, get_enac_experiment, case, roleouts,
                              in_cloud, minor)
    save_results(results, "ENAC", minor)


def main():
    ex5_1()
#    ex5_2()

if __name__ == "__main__":
    main()
    plot5_1()
