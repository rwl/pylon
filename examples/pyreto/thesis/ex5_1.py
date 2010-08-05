__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script runs the first experiment from chapter 5 of Learning to Trade
Power by Richard Lincoln. """

from numpy import zeros, mean, std

from pyreto import DISCRIMINATIVE

import pyreto.continuous
import pyreto.roth_erev #@UnusedImport

from pyreto.roth_erev import VariantRothErev

from pybrain.rl.explorers import BoltzmannExplorer #@UnusedImport
from pybrain.rl.learners import Q, QLambda, SARSA #@UnusedImport
from pybrain.rl.learners import ENAC, Reinforce #@UnusedImport

from common import \
    get_case6ww, setup_logging, get_discrete_task_agent, get_zero_task_agent, \
    run_experiment, save_result, get_continuous_task_agent, \
    get_neg_one_task_agent

from plot import plot5_1


setup_logging()

decommit = False
cap = 100.0
profile = [1.0]
nOffer = 1
nStates = 3

# Scale sigma manually?
manual_sigma = True

def get_re_experiment(case):
    """ Returns an experiment that uses the Roth-Erev learning method.
    """
    gen = case.generators
    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=DISCRIMINATIVE)

    experimentation=0.55
    recency=0.3
    epsilon=100.0
    decay=0.95#9995

    ##learner1 = pyreto.roth_erev.RothErev(experimentation=0.55, recency=0.3)
    learner1 = VariantRothErev(experimentation, recency)
    learner1.explorer = BoltzmannExplorer(epsilon, decay)
    task1, agent1 = get_discrete_task_agent(
        gen[:1], market, nStates, nOffer, (0, 10, 20, 30), profile, learner1)

    task2, agent2 = get_zero_task_agent(gen[1:2], market, nOffer, profile)

    learner3 = VariantRothErev(experimentation, recency)
    learner3.explorer = BoltzmannExplorer(epsilon, decay)
    task3, agent3 = get_discrete_task_agent(
        gen[2:3], market, nStates, nOffer, (0, 10, 20, 30), profile, learner3)

    experiment = pyreto.continuous.MarketExperiment(
        [task1, task2, task3], [agent1, agent2, agent3], market, profile)

    return experiment


def get_q_experiment(case):
    """ Returns an experiment that uses Q-learning.
    """
    gen = case.generators
    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit,
                                auctionType=DISCRIMINATIVE)

    alpha = 0.3 # Learning rate.
    gamma = 0.99 # Discount factor
    # The closer epsilon gets to 0, the more greedy and less explorative.
    epsilon = 0.5
    decay = 0.995#88
    tau = 150.0 # Boltzmann temperature.

    learner1 = Q(alpha, gamma)
#    learner1 = QLambda(alpha, gamma, qlambda=0.9)
#    learner1 = SARSA(alpha, gamma)

    learner1.explorer.epsilon = epsilon
    learner1.explorer.decay = decay
#    learner1.explorer = BoltzmannExplorer(tau, decay)

    task1, agent1 = get_discrete_task_agent(
        gen[:1], market, nStates, nOffer, (0, 10, 20, 30), profile, learner1)


    # Passive agent.
    task2, agent2 = get_zero_task_agent(gen[1:2], market, nOffer, profile)


    learner2 = Q(alpha, gamma)
#    learner2 = QLambda(alpha, gamma, qlambda=0.9)
#    learner2 = SARSA(alpha, gamma)

    learner2.explorer.epsilon = epsilon
    learner2.explorer.decay = decay
#    learner2.explorer = BoltzmannExplorer(tau, decay)

    task3, agent3 = get_discrete_task_agent(
        gen[2:3], market, nStates, nOffer, (0, 10, 20, 30), profile, learner2)

    experiment = pyreto.continuous.MarketExperiment(
        [task1, task2, task3], [agent1, agent2, agent3], market, profile)

    return experiment


def get_enac_experiment(case):
    gen = case.generators

    market = pyreto.SmartMarket(case, priceCap=cap, decommit=decommit)
    experiment = pyreto.continuous.MarketExperiment([], [], market, profile)

    for g in [gen[0], gen[2]]:
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

        markupMax = 30.0
        task, agent = get_continuous_task_agent(
            [g], market, nOffer, markupMax, profile, learner)

        # Adjust some parameters of the NormalExplorer.
        if manual_sigma:
            sigma = [-5.0] * task.env.indim
            agent.learner.explorer.sigma = sigma

        experiment.tasks.append(task)
        experiment.agents.append(agent)

    task, agent = get_neg_one_task_agent(gen[1:2], market, nOffer, profile)
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

    expts = 3
    roleouts = 100
    in_cloud = False

    expt_action_mean, expt_action_std, \
    expt_reward_mean, expt_reward_std, epsilon = \
        run_experiments(expts, get_re_experiment, case, roleouts, in_cloud)

    save_result(expt_action_mean, "./out/ex5_1_re_action_mean.mtx",
                "Experiment 5.1 Roth-Erev actions mean.")
    save_result(expt_action_std, "./out/ex5_1_re_action_std.mtx",
                "Experiment 5.1 Roth-Erev actions SD.")
    save_result(expt_reward_mean, "./out/ex5_1_re_reward_mean.mtx",
                "Experiment 5.1 Roth-Erev rewards mean.")
    save_result(expt_reward_std, "./out/ex5_1_re_reward_std.mtx",
                "Experiment 5.1 Roth-Erev rewards SD.")
    save_result(epsilon, "./out/ex5_1_re_epsilon.mtx",
                "Experiment 5.1 Roth-Erev learning rates.")


    expt_action_mean, expt_action_std, \
    expt_reward_mean, expt_reward_std, epsilon = \
        run_experiments(expts, get_q_experiment, case, roleouts, in_cloud)

    save_result(expt_action_mean, "./out/ex5_1_q_action_mean.mtx",
                "Experiment 5.1 Q-learning actions mean.")
    save_result(expt_action_std, "./out/ex5_1_q_action_std.mtx",
                "Experiment 5.1 Q-learning actions SD.")
    save_result(expt_reward_mean, "./out/ex5_1_q_reward_mean.mtx",
                "Experiment 5.1 Q-learning rewards mean.")
    save_result(expt_reward_std, "./out/ex5_1_q_reward_std.mtx",
                "Experiment 5.1 Q-learning rewards SD.")
    save_result(epsilon, "./out/ex5_1_q_epsilon.mtx",
                "Experiment 5.1 Q-learning learning rates.")


#    enac_experiment = get_enac_experiment(case)
#    action, reward = run_experiment(enac_experiment, roleouts, samples,
#                                    in_cloud)
#    save_result(action, "./out/ex5_1_enac_action.mtx",
#                "Experiment 5.1 ENAC actions.")
#    save_result(reward, "./out/ex5_1_enac_reward.mtx",
#                "Experiment 5.1 ENAC rewards.")

if __name__ == "__main__":
    main()
    plot5_1()
