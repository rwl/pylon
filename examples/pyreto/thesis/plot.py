__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script creates the plots published in Learning to Trade Power by
Richard Lincoln. """

import matplotlib
#matplotlib.use('WXAgg')#'TkAgg')

#matplotlib.rc('font', **{'family': 'sans-serif',
#                         'sans-serif': ['Computer Modern Sans serif']})
#matplotlib.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
#matplotlib.rc('text', usetex=True)

import random

from pylab import \
    figure, plot, xlabel, ylabel, legend, savefig, rcParams, clf, title, \
    xlim, ylim, show, errorbar, subplot, twinx, subplots_adjust, grid, gca

from matplotlib.ticker import IndexLocator, FixedLocator

from scipy import arange, sqrt, zeros, mean, std, r_
from scipy.io import mmread

from common import \
    get_winter_hourly, get_summer_hourly, get_spring_autumn_hourly, \
    get_weekly, get_daily

tex = False
paper = False

if not paper:
    matplotlib.rcParams['lines.linewidth'] = 0.5
    matplotlib.rcParams['axes.linewidth'] = 0.7

if tex:
    # Set up publication quality graphs.
    matplotlib.rc('font', **{'family': 'serif',
                             'serif': ['Computer Modern Roman']})

    if paper:
        fig_width = 6.15 # width in inches
        fig_height = 8.5 # height in inches
        params = {'backend': 'ps',
                  'axes.titlesize': 12,
                  'axes.labelsize': 10,
                  'text.fontsize': 10,
                  'legend.fontsize': 10,
                  'xtick.labelsize': 10,
                  'ytick.labelsize': 10,
                  'text.usetex': True,
                  'figure.figsize': [fig_width, fig_height]}
        rcParams.update(params)
    else:
        #fig_width_pt = 246.0  # Get this from LaTeX using \showthe\columnwidth
        #inches_per_pt = 1.0 / 72.27               # Convert pt to inch
        golden_mean = (sqrt(5) - 1.0) / 2.0 # Aesthetic ratio
        fig_width = 6.15#fig_width_pt * inches_per_pt  # width in inches
        fig_height = 10.0#fig_width * golden_mean      # height in inches
        fig_size = [fig_width, fig_height]
        params = {'backend': 'ps',
                  'axes.titlesize': 10,
                  'axes.labelsize': 10,
                  'text.fontsize': 10,
                  'legend.fontsize': 8,
                  'xtick.labelsize': 8,
                  'ytick.labelsize': 8,
                  'text.usetex': True,
        #          'markup': 'tex',
        #          'text.latex.unicode': True,
                  'figure.figsize': fig_size}
        rcParams.update(params)
else:
    params = {'axes.titlesize': 10,
              'axes.labelsize': 10,
              'text.fontsize': 8,
              'legend.fontsize': 8,
              'xtick.labelsize': 8,
              'ytick.labelsize': 8,
              'figure.figsize': (8, 10)}
    rcParams.update(params)


clr = ["black", "0.5", "0.8"]
ls = ["-"]#, ":", "--", "-."]
nc, ns = len(clr), len(ls)


def plot_results(results, ai, ylab, xlab="Time (h)"):
    nplot = len(results)

    for i, (result_mean, result_std, epsilon, lab, y2lab, y2max, y2min) in \
    enumerate(results):

        subplot(nplot, 1, i + 1)

        title(lab)

        x = arange(0.0, result_mean.shape[1], 1.0)
        y = result_mean[ai, :]
        e = result_std[ai, :]
        y2 = epsilon[ai, :]

#        plot(x, result_mean[ai, :],
#             color=clr[ai % nc],
#             linestyle=ls[ai % ns],
#             label=lab)

        errorbar(x, y, yerr=e, fmt='ko', linestyle="None",
                 label="Action/Reward",
                 capsize=0, markersize=3)#, linewidth=0.2)
        ylabel(ylab)

#        l = legend(loc="upper right")
#        l.get_frame().set_linewidth(0.5)

        # Exploration rate plot.
        twinx()
        plot(x, y2, color="black", label=y2lab)
        ylabel(y2lab)
        if y2max is not None:
            ylim(ymax=y2max)
        if y2min is not None:
            ylim(ymin=y2min)

#        l = legend(loc="lower right")
#        l.get_frame().set_linewidth(0.5)

#        subplots_adjust(left=0.09, bottom=0.05, right=None,
#                        wspace=None, hspace=None)

    xlabel(xlab)


def plot5_X(minor):
    re_epsilon = mmread("./out/ex5_%d_rotherev_epsilon.mtx" % minor)
    q_epsilon = mmread("./out/ex5_%d_q_epsilon.mtx" % minor)
    reinforce_epsilon = mmread("./out/ex5_%d_reinforce_epsilon.mtx" % minor)
    enac_epsilon = mmread("./out/ex5_%d_enac_epsilon.mtx" % minor)

    re_action_mean = mmread("./out/ex5_%d_rotherev_action_mean.mtx" % minor)
    re_action_std = mmread("./out/ex5_%d_rotherev_action_std.mtx" % minor)
    q_action_mean = mmread("./out/ex5_%d_q_action_mean.mtx" % minor)
    q_action_std = mmread("./out/ex5_%d_q_action_std.mtx" % minor)
    reinforce_action_mean = \
        mmread("./out/ex5_%d_reinforce_action_mean.mtx" % minor)
    reinforce_action_std = \
        mmread("./out/ex5_%d_reinforce_action_std.mtx" % minor)
    enac_action_mean = mmread("./out/ex5_%d_enac_action_mean.mtx" % minor)
    enac_action_std = mmread("./out/ex5_%d_enac_action_std.mtx" % minor)

    actions = [
        (re_action_mean, re_action_std, re_epsilon,
         "Roth-Erev", "Boltzmann Temperature", None, None),
        (q_action_mean, q_action_std, q_epsilon,
         "Q-Learning", "Epsilon", 1.0, 0.0),
        (reinforce_action_mean, reinforce_action_std, reinforce_epsilon,
         "REINFORCE", "Sigma", None, None),
        (enac_action_mean, enac_action_std, enac_epsilon,
         "ENAC", "Sigma", None, None)
    ]

    for ai in [0, 1]:
        figure(ai)
        plot_results(actions, ai, "Action (\%)")
        if tex:
            savefig('./out/fig5_%d_action_a%d.pdf' % (minor, ai + 1))
#            savefig('./out/fig5_%d_action_a%d.eps' % (minor, ai + 1))
        else:
            savefig('./out/fig5_%d_action_a%d.png' % (minor, ai + 1))


    re_reward_mean = mmread("./out/ex5_%d_rotherev_reward_mean.mtx" % minor)
    re_reward_std = mmread("./out/ex5_%d_rotherev_reward_std.mtx" % minor)
    q_reward_mean = mmread("./out/ex5_%d_q_reward_mean.mtx" % minor)
    q_reward_std = mmread("./out/ex5_%d_q_reward_std.mtx" % minor)
    reinforce_reward_mean = \
        mmread("./out/ex5_%d_reinforce_reward_mean.mtx" % minor)
    reinforce_reward_std = \
        mmread("./out/ex5_%d_reinforce_reward_std.mtx" % minor)
    enac_reward_mean = mmread("./out/ex5_%d_enac_reward_mean.mtx" % minor)
    enac_reward_std = mmread("./out/ex5_%d_enac_reward_std.mtx" % minor)

    rewards = [
        (re_reward_mean, re_reward_std, re_epsilon,
         "Roth-Erev", "Boltzmann Temperature", None, None),
        (q_reward_mean, q_reward_std, q_epsilon,
         "Q-Learning", "Epsilon", 1.0, 0.0),
        (reinforce_reward_mean, reinforce_reward_std, reinforce_epsilon,
         "REINFORCE", "Sigma", None, None),
        (enac_reward_mean, enac_reward_std, enac_epsilon,
         "ENAC", "Sigma", None, None)
    ]

    for ai in [0, 1]:
        figure(ai + 10)
        plot_results(rewards, ai, r"Reward (\verb+$+)")
        if tex:
            savefig('./out/fig5_%d_reward_a%d.pdf' % (minor, (ai + 1)))
#            savefig('./out/fig5_%d_reward_a%d.eps' % (minor, (ai + 1)))
        else:
            savefig('./out/fig5_%d_reward_a%d.png' % (minor, (ai + 1)))

#    if not tex:
#        show()


def plot5_1():
    plot5_X(1)


def plot5_2():
    plot5_X(2)


def plot_episodes(results, ai, ylab, xlab="Hour"):
    maxSteps = 24
    nplot = len(results)

    for i, (result_mean, result_std,
            passive_mean, passive_std, lab) in enumerate(results):

        ax = subplot(nplot, 1, i + 1)

#        title("Agent %d (%s)" % (ai + 1, lab))

        x = arange(0.0, maxSteps, 1.0)
        y = result_mean[ai, :]
        e = result_std[ai, :]
        py = passive_mean[ai, :]
        pe = passive_std[ai, :]
#        y2 = epsilon[ai, :]

#        plot(x, y,
#             color=clr[ai % nc],
#             linestyle=ls[ai % ns],
#             label=lab)

        errorbar(x, y, yerr=e, fmt='kx', linestyle="None",
                 label="Agent %d (%s)" % (ai + 1, lab),
                 capsize=3, markersize=5)#, linewidth=0.2)
        ylabel(ylab)

        errorbar(x, py, yerr=pe, fmt='ko', linestyle="None",
                 label="Marginal Cost",
                 capsize=1, markersize=3)#, linewidth=0.2)

        ax.ticklabel_format(style='sci', scilimits=(0,0), axis='y')

        xlim((0, 23))
        ax.yaxis.grid(True)
        locator = FixedLocator(range(0, 24))
        ax.xaxis.set_major_locator(locator)      #minor x-axis ticks

        l = legend(loc="upper left")
        l.get_frame().set_linewidth(0.5)

    xlabel(xlab)


def plot_agents(rewards, ylab, agents=[0,1,2,3], xlab="Hour"):
    maxSteps = 24
    nplots = len(agents)
    fmt = ["w^", "wo", "ks", "kv"]

    for i, ai in enumerate(agents):
        ax = subplot(nplots, 1, i + 1)
#        title("Agent %d" % (i + 1))
        ylabel(ylab)

        x = arange(0.0, maxSteps, 1.0)

        for j, (result_mean, _, _, _, lab) in enumerate(rewards):

            y = result_mean[i, :]

            plot(x, y, fmt[j], linestyle="None",
#                 markerfacecolor='white',
                 markersize=5,
#                 color=clr[ai % nc],
#                 linestyle=ls[ai % ns],
                 label="A%s (%s)" % (ai + 1, lab))

            ax.ticklabel_format(style='sci', scilimits=(0,0), axis='y')

            xlim((0, 23))
#            ax.yaxis.grid(True)
            locator = FixedLocator(range(0, 24))
            ax.xaxis.set_major_locator(locator)      #minor x-axis ticks

            l = legend(loc="upper left")
            l.get_frame().set_linewidth(0.5)

    xlabel(xlab)


def plot6_X(minor=1):
#    re_epsilon = mmread("./out/ex6_%d_rotherev_epsilon.mtx" % minor)
#    q_epsilon = mmread("./out/ex6_%d_q_epsilon.mtx" % minor)
#    reinforce_epsilon = mmread("./out/ex6_%d_reinforce_epsilon.mtx" % minor)
#    enac_epsilon = mmread("./out/ex6_%d_enac_epsilon.mtx" % minor)

    passive_reward_mean = mmread("./out/ex6_%d_passive_reward_mean.mtx" % minor)
    passive_reward_std = mmread("./out/ex6_%d_passive_reward_std.mtx" % minor)

#    re_reward_mean = mmread("./out/ex6_%d_rotherev_reward_mean.mtx" % minor)
#    re_reward_std = mmread("./out/ex6_%d_rotherev_reward_std.mtx" % minor)
    re_reward_mean = mmread("./out/ex6_%d_statefulre_reward_mean.mtx" % minor)
    re_reward_std = mmread("./out/ex6_%d_statefulre_reward_std.mtx" % minor)

    q_reward_mean = mmread("./out/ex6_%d_q_reward_mean.mtx" % minor)
    q_reward_std = mmread("./out/ex6_%d_q_reward_std.mtx" % minor)
    reinforce_reward_mean = \
        mmread("./out/ex6_%d_reinforce_reward_mean.mtx" % minor)
    reinforce_reward_std = \
        mmread("./out/ex6_%d_reinforce_reward_std.mtx" % minor)
    enac_reward_mean = mmread("./out/ex6_%d_enac_reward_mean.mtx" % minor)
    enac_reward_std = mmread("./out/ex6_%d_enac_reward_std.mtx" % minor)

    if False:
        def average(reward):
            na = reward.shape[0]
            maxSteps = 24

            reward_mean = zeros((na, maxSteps))
            reward_std = zeros((na, maxSteps))

            roleouts = 8 * 7 # num of final episodes to average
            episodes = 1
            reward = reward[:, -maxSteps * episodes * roleouts:]

            for s in range(maxSteps):
                reward_mean[:, s] = mean(reward[:, s::maxSteps], axis=1)
                reward_std[:, s] = std(reward[:, s::maxSteps], axis=1, ddof=1)

            return reward_mean, reward_std

        re_rewards = mmread("./out/ex6_%d_rotherev_all_rewards.mtx" % minor)
        enac_rewards = mmread("./out/ex6_%d_enac_all_rewards.mtx" % minor)

        re_reward_mean, re_reward_std = average(re_rewards)
        enac_reward_mean, enac_reward_std = average(enac_rewards)

    rewards = [
#        (passive_reward_mean, passive_reward_std, "Passive"),
        (re_reward_mean, re_reward_std,
         passive_reward_mean, passive_reward_std, "Roth-Erev"),
        (q_reward_mean, q_reward_std,
         passive_reward_mean, passive_reward_std, "Q-Learning"),
        (reinforce_reward_mean, reinforce_reward_std,
         passive_reward_mean, passive_reward_std, "REINFORCE"),
        (enac_reward_mean, enac_reward_std,
         passive_reward_mean, passive_reward_std, "ENAC")
    ]

#    for ai in range(4):
#        figure(ai + 10)
#        plot_episodes(rewards, ai, r"Reward (\verb+$+)")
#        if tex:
#            savefig('./out/fig6_%d_reward_a%d.pdf' % (minor, (ai + 1)))
##            savefig('./out/fig6_%d_reward_a%d.eps' % (minor, (ai + 1)))
#        else:
#            savefig('./out/fig6_%d_reward_a%d.png' % (minor, (ai + 1)))


    figure(909)
    plot_agents(rewards, r"Reward (\verb+$+)")
    savefig('./out/fig6_%d_rewards.png' % minor)

#    if not tex:
#        show()


def plot6_0():
    plot6_X(1)


def plot6_1():
    fig_width = 6.15 # width in inches
    fig_height = 5.0 # height in inches
    params = {'figure.figsize': [fig_width, fig_height]}
    rcParams.update(params)

    re_mean = mmread("./out/ex6_1/ex6_1_rotherev_reward_mean.mtx")
    sre_mean = mmread("./out/ex6_1/ex6_1_statefulre_reward_mean.mtx")
    q_mean = mmread("./out/ex6_1/ex6_1_q_reward_mean.mtx")

    rewards = [
        (re_mean, None, None, None, "Roth-Erev"),
        (q_mean, None, None, None, "Q-Learning"),
        (sre_mean, None, None, None, "Stateful RE")
    ]
    figure()
    plot_agents(rewards, r"Reward (\verb+$+)", agents=[1, 3])
    savefig('./out/ex6_1/fig6_1.png')


def plot6_2():
    q1 = mmread("./out/ex6_2/ex6_2-1_q_reward_mean.mtx")
    reinforce1 = mmread("./out/ex6_2/ex6_2-1_reinforce_reward_mean.mtx")
    enac1 = mmread("./out/ex6_2/ex6_2-1_enac_reward_mean.mtx")

#    q2 = mmread("./out/ex6_2/ex6_2-2_q_reward_mean.mtx")
    reinforce2 = mmread("./out/ex6_2/ex6_2-2_reinforce_reward_mean.mtx")
    enac2 = mmread("./out/ex6_2/ex6_2-2_enac_reward_mean.mtx")

    maxSteps = 24
    nplots = 4
    fmt = ["wo", "ks", "kv"]

    x = arange(0.0, maxSteps, 1.0)

    def plot62(results, i, n):
        ax = subplot(nplots, 1, n)

        for k, (r, lab) in enumerate(results):
            plot(x, r[i, :], fmt[k], linestyle="None", markersize=5, label=lab)

        ax.ticklabel_format(style='sci', scilimits=(0,0), axis='y')

        xlim((0, 23))
        locator = FixedLocator(range(0, 24))
        ax.xaxis.set_major_locator(locator)      #minor x-axis ticks

        ylabel(r"Reward (\verb+$+)")

        l = legend(loc="upper left")
        l.get_frame().set_linewidth(0.5)

    results1 = [(q1, "Q"), (reinforce1, "REINFORCE"), (enac1, "ENAC")]
    results2 = [(q1, "Q"), (reinforce2, "REINFORCE"), (enac2, "ENAC")]

    figure()
    plot62(results1, i=1, n=1)
    title("Agent 2 with demand only state")
    plot62(results2, i=1, n=2)
    title("Agent 2 with demand and bus voltage state")
#    xlabel("Hour")
#    savefig('./out/ex6_2/fig6_2_agent2.png')

#    figure()
    plot62(results1, i=3, n=3)
    title("Agent 4 with demand only state")
    plot62(results2, i=3, n=4)
    title("Agent 4 with demand and bus voltage state")
    xlabel("Hour")
#    savefig('./out/ex6_2/fig6_2_agent4.png')
    savefig('./out/ex6_2/fig6_2.png')


def plot_profiles():
    figure()
    subplot(3, 1, 1)
#    clf()
    x = arange(0.0, 52.0, 1.0)
    plot(x, get_weekly(), color="black")
    xlabel("Week of the year (starting January 1st)")
    ylabel("\% of annual peak load")
    xlim((0.0, 51.0))
    ylim((0.0, 100.0))
    title("IEEE RTS Weekly Load Profile")
    legend()
    grid()
#    savefig('./out/ieee_rts_weekly.pdf')


    subplot(3, 1, 2)
#    clf()
    x = arange(1.0, 8.0, 1.0)
    plot(x, get_daily(), color="black")
    xlabel("Day of the week (starting on Monday)")
    ylabel("\% of weekly peak load")
    xlim((1.0, 7.0))
    ylim((0.0, 100.0))
    title("IEEE RTS Daily Load Profile")
    legend()
    grid()
#    savefig('./out/ieee_rts_daily.pdf')


    subplot(3, 1, 3)
#    clf()
    hourly_winter_wkdy, hourly_winter_wknd = get_winter_hourly()
    hourly_summer_wkdy, hourly_summer_wknd = get_summer_hourly()
    hourly_spring_autumn_wkdy, hourly_spring_autumn_wknd = \
        get_spring_autumn_hourly()

    x = arange(0.0, 24.0, 0.5)

    plot(x, r_[hourly_winter_wkdy, hourly_winter_wknd],
         label="Winter (Weeks 1-8 \& 44-52)", color="black")
    plot(x, r_[hourly_summer_wkdy, hourly_summer_wknd],
         label="Summer (Weeks 18-30)", color="0.4")
    plot(x, r_[hourly_spring_autumn_wkdy, hourly_spring_autumn_wknd],
         label="Spring \& Autumn (Weeks 9-17 \& 31-43)", color="0.6")

    xlabel("Hour of the day (starting at midnight)")
    ylabel("\% of daily peak load")
    xlim((0.0, 23.0))
    ylim((0.0, 100.0))
    title("IEEE RTS Hourly Load Profiles")
    l = legend(loc="lower right")
#    l.get_frame().set_linewidth(0.7)
    grid()
#    savefig('./out/ieee_rts_hourly.pdf')

    subplots_adjust(hspace=0.35)

    savefig('./out/ieee_rts_profiles.pdf')


if __name__ == "__main__":
#    plot5_1()
#    plot5_2()
    plot6_0()
#    plot6_1()
#    plot6_2()
#    plot_profiles()
