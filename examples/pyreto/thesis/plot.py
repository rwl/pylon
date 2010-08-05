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
    xlim, ylim, show, errorbar, subplot, twinx

from scipy import arange, sqrt
from scipy.io import mmread

from common import \
    get_winter_hourly, get_summer_hourly, get_spring_autumn_hourly, \
    get_weekly, get_daily

matplotlib.rcParams['lines.linewidth'] = 0.5
matplotlib.rcParams['axes.linewidth'] = 0.7
matplotlib.rcParams['axes.titlesize'] = "medium"

tex = True

if tex:
    # Set up publication quality graphs.
    matplotlib.rc('font', **{'family': 'serif',
                             'serif': ['Computer Modern Roman']})

    #fig_width_pt = 246.0  # Get this from LaTeX using \showthe\columnwidth
    #inches_per_pt = 1.0 / 72.27               # Convert pt to inch
    golden_mean = (sqrt(5) - 1.0) / 2.0 # Aesthetic ratio
    fig_width = 5.5#fig_width_pt * inches_per_pt  # width in inches
    fig_height = 7.0#fig_width * golden_mean      # height in inches
    fig_size = [fig_width, fig_height]
    params = {'backend': 'ps',
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


clr = ["black", "0.5", "0.8"]
ls = ["-"]#, ":", "--", "-."]
nc, ns = len(clr), len(ls)


def plot_results(results, gi, ylab, xlab="Time (h)"):
    figure(random.randint(0, 100))

    nplot = len(results)
    for i, (result_mean, result_std, epsilon, lab, y2lab, y2max, y2min) in \
    enumerate(results):
        subplot(nplot, 1, i + 1)

        title(lab)

        x = arange(0.0, result_mean.shape[1], 1.0)
        y = result_mean[gi, :]
        e = result_std[gi, :]
        y2 = epsilon[gi, :]

#        plot(x, result_mean[gi, :],
#             color=clr[gi % nc],
#             linestyle=ls[gi % ns],
#             label=lab)

        ax1 = errorbar(x, y, yerr=e, fmt='ko', linestyle="None", label=lab,
                       capsize=2, markersize=3)#, linewidth=0.2)
        ylabel(ylab)

        l = legend(loc="upper right")
        l.get_frame().set_linewidth(0.5)

        # Exploration rate plot.
        twinx()
        plot(x, y2, color="black", label=y2lab)
        ylabel(y2lab)
        if y2max is not None:
            ylim(ymax=y2max)
        if y2min is not None:
            ylim(ymin=y2min)

        l = legend(loc="lower right")
        l.get_frame().set_linewidth(0.5)
    xlabel(xlab)


def plot5_1():
    re_epsilon = mmread("./out/ex5_1_re_epsilon.mtx")
    q_epsilon = mmread("./out/ex5_1_q_epsilon.mtx")

    re_action_mean = mmread("./out/ex5_1_re_action_mean.mtx")
    re_action_std = mmread("./out/ex5_1_re_action_std.mtx")
    q_action_mean = mmread("./out/ex5_1_q_action_mean.mtx")
    q_action_std = mmread("./out/ex5_1_q_action_std.mtx")
#    enac_action = mmread("./out/ex5_1_enac_action.mtx")

    actions = [
       (re_action_mean, re_action_std, re_epsilon,
        "Roth-Erev", "Boltzmann Temperature", None, None),
       (q_action_mean, q_action_std, q_epsilon,
        "Q-Learning", "Epsilon", 1.0, 0.0),
#       (enac_action, "ENAC")
    ]

    plot_results(actions, 0, "Action (\%)")
#    title("Generator 1 Action")
    if tex:
        savefig('./out/fig5_1_g1_action.pdf')
    plot_results(actions, 2, "Action (\%)")
#    title("Generator 2 Action")
    if tex:
        savefig('./out/fig5_1_g3_action.pdf')


#    re_reward_mean = mmread("./out/ex5_1_re_reward_mean.mtx")
#    re_reward_std = mmread("./out/ex5_1_re_reward_std.mtx")
#    q_reward_mean = mmread("./out/ex5_1_q_reward_mean.mtx")
#    q_reward_std = mmread("./out/ex5_1_q_reward_std.mtx")
##    enac_reward = mmread("./out/ex5_1_enac_reward.mtx")
#
#    rewards = [
#        (re_reward_mean, re_reward_std, re_epsilon, "Roth-Erev"),
#        (q_reward_mean, q_reward_std, q_epsilon, "Q-Learning"),
##        (enac_reward, "ENAC")
#    ]
#
#    plot_results(rewards, 0, r"Reward (\verb+$+)")
##    title("Generator 1 Reward")
#    if tex:
#        savefig('./out/fig5_1_g1_reward.pdf')
#    plot_results(rewards, 2, r"Reward (\verb+$+)")
##    title("Generator 2 Reward")
#    if tex:
#        savefig('./out/fig5_1_g3_reward.pdf')

    if not tex:
        show()


def plot_profiles():
    figure()
    clf()
    x = arange(0.0, 52.0, 1.0)
    plot(x, get_weekly(), color="black")
    xlabel("Week of the year, starting January 1st")
    ylabel("Percentage of annual peak load")
    xlim((0.0, 51.0))
    ylim((0.0, 100.0))
#    title("IEEE RTS Weekly Load Profile")
    legend()
    savefig('./out/ieee_rts_weekly.pdf')


    clf()
    x = arange(1.0, 8.0, 1.0)
    plot(x, get_daily(), color="black")
    xlabel("Day of the week, starting Monday")
    ylabel("Percentage of weekly peak load")
    xlim((1.0, 7.0))
    ylim((0.0, 100.0))
#    title("IEEE RTS Daily Load Profile")
    legend()
    savefig('./out/ieee_rts_daily.pdf')


    clf()
    hourly_winter_wkdy, hourly_winter_wknd = get_winter_hourly()
    hourly_summer_wkdy, hourly_summer_wknd = get_summer_hourly()
    hourly_spring_autumn_wkdy, hourly_spring_autumn_wknd = \
        get_spring_autumn_hourly()

    x = arange(0.0, 24.0, 0.5)

    plot(x, hourly_winter_wkdy + hourly_winter_wknd,
         label="Winter (Weeks 1-8 \& 44-52)", color="black")
    plot(x, hourly_summer_wkdy + hourly_summer_wknd,
         label="Summer (Weeks 18-30)", color="0.4")
    plot(x, hourly_spring_autumn_wkdy + hourly_spring_autumn_wknd,
         label="Spring \& Autumn (Weeks 9-17 \& 31-43)", color="0.6")

    xlabel("Hour of the day, starting at midnight")
    ylabel("Percentage of daily peak load")
    xlim((0.0, 23.0))
    ylim((0.0, 100.0))
#    title("IEEE RTS Hourly Load Profiles")
    legend(loc="lower right")

    savefig('./out/ieee_rts_hourly.pdf')


if __name__ == "__main__":
    plot5_1()
#    plot_profiles()
