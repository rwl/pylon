#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

""" Defines a renderer that is executed as a concurrent thread and displays
    aspects of the environment.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import threading

from numpy import zeros
from pylab import ion, figure, draw, plot, clf, title

from pybrain.rl.environments.renderer import Renderer

#------------------------------------------------------------------------------
#  "ParticipantRenderer" class:
#------------------------------------------------------------------------------

class ParticipantRenderer(Renderer):
    """ Defines a renderer that displays aspects of a market participant's
        environment.
    """
    def __init__(self):
        """ Initialises a new ParticipantRenderer instance.
        """
        super(ParticipantRenderer, self).__init__()

        self.dataLock = threading.Lock()
#        self.demand = 0.0
#        self.price  = 0.0
#        self.profit = 0.0
#        self.weight = 0.0

        self.updates = 0
        self.plots = zeros((1000, 4), float)


    def updateData(self, data):
        """ Updates the data used by the renderer.
        """
        self.dataLock.acquire()
        demand, price, profit, weight = data
        self.plots[self.updates, 0] = demand
        self.plots[self.updates, 1] = price
        self.plots[self.updates, 2] = profit
        self.plots[self.updates, 3] = weight
        self.updates += 1
        self.dataLock.release()


    def start(self):
        """ Wrapper for Thread.start().
        """
        self.draw_plot()
        super(ParticipantRenderer, self).start()


    def draw_plot(self):
        """ Initialises plots of the environment.
        """
        ion()
        self.state_fig = figure()
#        clf()
        title('State')


    def _render(self):
        """ Calls the render methods.
        """
        self.dataLock.acquire()
        figure(self.state_fig.number)
        plot(self.plots[0:self.updates, 0])
        draw()
        self.dataLock.release()

# EOF -------------------------------------------------------------------------
