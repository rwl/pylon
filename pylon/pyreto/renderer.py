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

import time
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
#        super(ParticipantRenderer, self).__init__()
        Renderer.__init__(self)

        self.dataLock = threading.Lock()
        self.stopRequest = False

#        self.demand = 0.0
#        self.price  = 0.0
#        self.profit = 0.0
#        self.weight = 0.0

        self.updates = 0
        self.plots = zeros((1000, 4), float)


    def updateData(self, data, increment=True):
        """ Updates the data used by the renderer.
        """
        self.dataLock.acquire()
        if data[0] is not None:
            self.plots[self.updates, 0] = data[0] # demand
        if data[1] is not None:
            self.plots[self.updates, 1] = data[1] # price
        if data[2] is not None:
            self.plots[self.updates, 2] = data[2] # profit
        if data[3] is not None:
            self.plots[self.updates, 3] = data[3] # weight
        if increment:
            self.updates += 1
        self.dataLock.release()


    def start(self):
        """ Wrapper for Thread.start().
        """
        self.draw_plot()
#        super(ParticipantRenderer, self).start()
        Renderer.start(self)


    def stop(self):
        """ Stops the current thread.
        """
        self.dataLock.acquire()
        self.stopRequest = True
        self.dataLock.release()


    def draw_plot(self):
        """ Initialises plots of the environment.
        """
        ion()
#        self.state_fig = figure(1)
#        clf()
#        title('State')


    def _render(self):
        """ Calls the render methods.
        """
        while not self.stopRequest:
            self.dataLock.acquire()
            figure(1)#self.state_fig.number)
#            clf()
            plot(self.plots[0:self.updates, 0], "g+-")
            plot(self.plots[0:self.updates, 1], "ro-")
            plot(self.plots[0:self.updates, 2], "mx-")
            plot(self.plots[0:self.updates, 3], "k-")
            draw()
            self.dataLock.release()

            time.sleep(0.05)
        self.stopRequest = False

# EOF -------------------------------------------------------------------------
