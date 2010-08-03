__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

""" This script creates the plots published in Learning to Trade Power by
Richard Lincoln. """

import matplotlib
#matplotlib.use('WXAgg')#'TkAgg')

#matplotlib.rc('font', **{'family': 'sans-serif',
#                         'sans-serif': ['Computer Modern Sans serif']})
matplotlib.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
matplotlib.rc('text', usetex=True)

from pylab import \
    figure, plot, xlabel, ylabel, legend, savefig, rcParams, clf, title, \
    xlim, ylim

from scipy import arange, sqrt
from scipy.io import mmread

from common import \
    get_winter_hourly, get_summer_hourly, get_spring_autumn_hourly, \
    get_weekly, get_daily

# Set up publication quality graphs.
#fig_width_pt = 246.0  # Get this from LaTeX using \showthe\columnwidth
#inches_per_pt = 1.0 / 72.27               # Convert pt to inch
golden_mean = (sqrt(5) - 1.0) / 2.0 # Aesthetic ratio
fig_width = 5.5#fig_width_pt * inches_per_pt  # width in inches
fig_height = fig_width * golden_mean      # height in inches
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
    figure()
    clf()
    for (result, lab) in results:
        x = arange(0.0, result.shape[1], 1.0)
        plot(x, result[gi, :],
#             color=clr[gi % nc],
#             linestyle=ls[gi % ns],
             label=lab)
    xlabel(xlab)
    ylabel(ylab)
    legend()


def plot5_1():
    re_action = mmread("./out/ex5_1_re_action.mtx")
    q_action = mmread("./out/ex5_1_q_action.mtx")
    enac_action = mmread("./out/ex5_1_enac_action.mtx")

    actions = [(re_action, "Roth-Erev"), (q_action, "Q-Learning"),
               (enac_action, "ENAC")]

    plot_results(actions, 0, "Action (\%)")
#    title("Generator 1 Action")
    savefig('./out/fig5_1_g1_action.pdf')
    plot_results(actions, 2, "Action (\%)")
#    title("Generator 2 Action")
    savefig('./out/fig5_1_g3_action.pdf')


    re_reward = mmread("./out/ex5_1_re_reward.mtx")
    q_reward = mmread("./out/ex5_1_q_reward.mtx")
    enac_reward = mmread("./out/ex5_1_enac_reward.mtx")

    rewards = [(re_reward, "Roth-Erev"), (q_reward, "Q-Learning"),
               (enac_reward, "ENAC")]

    plot_results(rewards, 0, r"Reward (\verb+$+)")
#    title("Generator 1 Reward")
    savefig('./out/fig5_1_g1_reward.pdf')
    plot_results(rewards, 2, r"Reward (\verb+$+)")
#    title("Generator 2 Reward")
    savefig('./out/fig5_1_g3_reward.pdf')


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
