#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Defines plotting tools.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import scipy

from itertools import count, izip
from pylab import figure, xlabel, ylabel, plot, show, legend

from pylon.generator import PW_LINEAR, POLYNOMIAL

#------------------------------------------------------------------------------
#  "plot_gen_cost" function:
#------------------------------------------------------------------------------

def plot_gen_cost(generators):
    """ Plots the costs of the given generators.
    """
    figure()
    plots = []
    for generator in generators:

        print generator.p_cost

        if generator.pcost_model == PW_LINEAR:
            x = [x for x, _ in generator.p_cost]
            y = [y for _, y in generator.p_cost]
        elif generator.pcost_model == POLYNOMIAL:
            x = scipy.arange(0., generator.p_max, 5)
            y = scipy.polyval(scipy.array(generator.p_cost), x)
        else:
            raise
        plots.append(plot(x, y))
        xlabel("P (MW)")
        ylabel("Cost ($)")
    legend(plots, [g.name for g in generators])
    show()

#------------------------------------------------------------------------------
#  "sparkline_data" function:
#------------------------------------------------------------------------------

def sparkline_data(data, filename):
    """ Writes reward and action data for plotting sparklines with PGF/TikZ.

        @see: http://www.texample.net/tikz/examples/weather-stations-data/
    """
    fd = file(filename, "w+b")
    for name in data.keys():
        action, reward = data[name]

        alt_name = name.lower().replace("_", "")

        fd.write("\def")
        fd.write("\REWARDDATA%s{" % alt_name)
        for i, r in enumerate(reward):
            fd.write("(%.2f,%.3f)" % (i / 10.0, r / 10.0)) # dimension too large
        fd.write("}\n")

        maxreward, maxindex = max(izip(reward, count()))
        minreward, minindex = min(izip(reward, count()))
        meanreward = scipy.mean(reward)
        fd.write("\def\REWARDMAX%s{%.1f}\n" % (alt_name, maxreward))
        fd.write("\def\REWARDMAXIDX%s{%d}\n" % (alt_name, maxindex))
        fd.write("\def\REWARDMIN%s{%.1f}\n" % (alt_name, minreward))
        fd.write("\def\REWARDMINIDX%s{%d}\n" % (alt_name, minindex))
        fd.write("\def\REWARDMEAN%s{%.1f}\n" % (alt_name, meanreward))

        fd.write("\def")
        fd.write("\ACTIONDATA%s{" % alt_name)
        for i, a in enumerate(action):
            fd.write("(%.2f,%.3f)" % (i / 10.0, a / 10.0))
        fd.write("}\n")

        maxaction, maxindex = max(izip(reward, count()))
        minaction, minindex = min(izip(reward, count()))
        meanaction = scipy.mean(reward)
        fd.write("\def\ACTIONMAX%s{%.1f}\n" % (alt_name, maxaction))
        fd.write("\def\ACTIONMAXIDX%s{%d}\n" % (alt_name, maxindex))
        fd.write("\def\ACTIONMIN%s{%.1f}\n" % (alt_name, minaction))
        fd.write("\def\ACTIONMINIDX%s{%d}\n" % (alt_name, minindex))
        fd.write("\def\ACTIONMEAN%s{%.1f}\n" % (alt_name, meanaction))
    fd.close()

# EOF -------------------------------------------------------------------------
