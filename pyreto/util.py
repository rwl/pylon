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

from pybrain.rl.agents.logging import LoggingAgent

from pylon.generator import PW_LINEAR, POLYNOMIAL

#------------------------------------------------------------------------------
#  "ZeroAgent" class:
#------------------------------------------------------------------------------

class ZeroAgent(LoggingAgent):

    def getAction(self):
        self.lastaction = -1.0 * scipy.ones(self.outdim)
        return self.lastaction

    def learn(self):
        pass

#------------------------------------------------------------------------------
#  "xselections" function:
#------------------------------------------------------------------------------

def xselections(items, n):
    """ Takes n elements (not necessarily distinct) from the sequence, order
        matters.

        @see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/190465
    """
    if n==0:
        yield []
    else:
        for i in xrange(len(items)):
            for ss in xselections(items, n-1):
                yield [items[i]]+ss

#------------------------------------------------------------------------------
#  "plotGenCost" function:
#------------------------------------------------------------------------------

def plotGenCost(generators):
    """ Plots the costs of the given generators.
    """
    figure()
    plots = []
    for generator in generators:
        if generator.pcost_model == PW_LINEAR:
            x = [x for x, _ in generator.p_cost]
            y = [y for _, y in generator.p_cost]
        elif generator.pcost_model == POLYNOMIAL:
            x = scipy.arange(generator.p_min, generator.p_max, 5)
            y = scipy.polyval(scipy.array(generator.p_cost), x)
        else:
            raise
        plots.append(plot(x, y))
        xlabel("P (MW)")
        ylabel("Cost ($)")
    legend(plots, [g.name for g in generators])
    show()

#------------------------------------------------------------------------------
#  "sparklineData" function:
#------------------------------------------------------------------------------

def sparklineData(data, filename):
    """ Writes reward and action data for plotting sparklines with PGF/TikZ.

        @see: http://www.texample.net/tikz/examples/weather-stations-data/
    """
    fd = file(filename, "w+b")
    for name in data.keys():
        action, reward = data[name]

        altName = name.lower().replace("_", "")

        fd.write("\def")
        fd.write("\REWARDDATA%s{" % altName)
        for i, r in enumerate(reward):
            fd.write("(%.2f,%.3f)" % (i / 10.0, r / 10.0)) # dimension too large
        fd.write("}\n")

        maxreward, maxindex = max(izip(reward, count()))
        minreward, minindex = min(izip(reward, count()))
        meanreward = scipy.mean(reward)
        fd.write("\def\REWARDMAX%s{%.1f}\n" % (altName, maxreward))
        fd.write("\def\REWARDMAXIDX%s{%d}\n" % (altName, maxindex))
        fd.write("\def\REWARDMIN%s{%.1f}\n" % (altName, minreward))
        fd.write("\def\REWARDMINIDX%s{%d}\n" % (altName, minindex))
        fd.write("\def\REWARDMEAN%s{%.1f}\n" % (altName, meanreward))

        fd.write("\def")
        fd.write("\ACTIONDATA%s{" % altName)
        for i, a in enumerate(action):
            fd.write("(%.2f,%.3f)" % (i / 10.0, a / 10.0))
        fd.write("}\n")

        maxaction, maxindex = max(izip(reward, count()))
        minaction, minindex = min(izip(reward, count()))
        meanaction = scipy.mean(reward)
        fd.write("\def\ACTIONMAX%s{%.1f}\n" % (altName, maxaction))
        fd.write("\def\ACTIONMAXIDX%s{%d}\n" % (altName, maxindex))
        fd.write("\def\ACTIONMIN%s{%.1f}\n" % (altName, minaction))
        fd.write("\def\ACTIONMINIDX%s{%d}\n" % (altName, minindex))
        fd.write("\def\ACTIONMEAN%s{%.1f}\n" % (altName, meanaction))
    fd.close()

#------------------------------------------------------------------------------
#  "ReSTExperimentWriter" class:
#------------------------------------------------------------------------------

class ReSTExperimentWriter(object):
    """ Writes market experiment data to file in ReStructuredText format.
    """

    def __init__(self, experiment):
        """ Initialises a new ReSTExperimentWriter instance.
        """
        # Market experiment whose data is to be written.
        self.experiment = None


    def write(self, file):
        """ Writes market experiment data to file in ReStructuredText format.
        """
        # Write environment state data.
        file.write("State\n")
        file.write( ("-" * 5) + "\n")
        self.writeDataTable(file, type="state")

        # Write action data.
        file.write("Action\n")
        file.write( ("-" * 6) + "\n")
        self.writeDataTable(file, type="action")

        # Write reward data.
        file.write("Reward\n")
        file.write( ("-" * 6) + "\n")
        self.writeDataTable(file, type="reward")


    def writeDataTable(self, file, type):
        """ Writes agent data to an ReST table.  The 'type' argument may
            be 'state', 'action' or 'reward'.
        """
        agents = self.experiment.agents
        numAgents = len(self.experiment.agents)

        colWidth = 8
        idxColWidth = 3

        sep = ("=" * idxColWidth) + " " + \
            ("=" * colWidth + " ") * numAgents + "\n"

        file.write(sep)

        # Table column headers.
        file.write("..".rjust(idxColWidth) + " ")
        for agent in agents:
            # The end of the name is typically the unique part.
            file.write(agent.name[-colWidth:].center(colWidth) + " ")
        file.write("\n")

        file.write(sep)

        # Table values.
        if agents:
            rows, _ = agents[0].history.getField( type ).shape
        else:
            rows, _ = (0, 0)

        for sequence in range( min(rows, 999) ):
            file.write( str(sequence + 1).rjust(idxColWidth) + " " )

            for agent in agents:
                field = agent.history.getField( type )
                # FIXME: Handle multiple state values.
                file.write("%8.3f " % field[sequence, 0])

            file.write("\n")

        file.write(sep)

# EOF -------------------------------------------------------------------------
