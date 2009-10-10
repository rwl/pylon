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

import matplotlib
matplotlib.use('WXAgg')

import numpy
import pylab

from pybrain.rl.environments.renderer import Renderer

#------------------------------------------------------------------------------
#  "ParticipantRenderer" class:
#------------------------------------------------------------------------------

class ParticipantRenderer(Renderer):
    """ Defines a renderer that displays aspects of a market participant's
        environment.
    """
    def __init__(self, outdim, indim, intermax=1000):
        """ Initialises a new ParticipantRenderer instance.
        """
        super(ParticipantRenderer, self).__init__()

#        self.dataLock = threading.Lock()
        self.stopRequest = False

        self.updates = 0

        self.state_data = numpy.zeros((outdim, intermax), float)
        self.action_data = numpy.zeros((indim, intermax), float)
        self.reward_data = numpy.zeros((1, intermax), float)

        self.state_lines = []
        self.action_lines = []
        self.reward_line = None

    #--------------------------------------------------------------------------
    #  "Renderer" interface:
    #--------------------------------------------------------------------------

    def updateData(self, state_data, action_data, reward_data):
        """ Updates the data used by the renderer.
        """
#        self.dataLock.acquire()

        self.state_data[:, self.updates] = state_data
        self.action_data[:, self.updates] = action_data
        self.reward_data[0, self.updates] = reward_data
        self.updates += 1
        self._render()

#        self.dataLock.release()


    def start(self):
        """ Wrapper for Thread.start().
        """
        self.draw_plot()
        super(ParticipantRenderer, self).start()


#    def stop(self):
#        """ Stops the current thread.
#        """
#        pass
#        self.dataLock.acquire()
#        self.stopRequest = True
#        self.dataLock.release()

    #--------------------------------------------------------------------------
    #  "ParticipantRenderer" interface:
    #--------------------------------------------------------------------------

    def draw_plot(self):
        """ Initialises plots of the environment.
        """
        pylab.ion()
        fig = pylab.figure(1)

        # State plot.
#        state_axis = fig.add_subplot(3, 1, 1) # numrows, numcols, fignum
#        state_axis.title = 'State'
#        state_axis.xlabel = 'Time (hours)'
#        state_axis.grid = True
#        for i in range(self.state_data.shape[0]):
#            lines = state_axis.plot(self.state_data[i, 0], "g+-")
#            self.state_lines.append(lines[0])

        # Action plot.
#        action_axis = fig.add_subplot(3, 1, 2)
#        action_axis.title = 'Action'
#        action_axis.xlabel = 'Time (hours)'
#        action_axis.ylabel = 'Price ($/MWh)'
#        action_axis.grid = True
#        for i in range(self.action_data.shape[0]):
#            lines = action_axis.plot(self.action_data[i, 0], "ro-")
#            self.action_lines.append(lines[0])

        # Reward plot.
        reward_axis = fig.add_subplot(3, 1, 3)
#        reward_axis.title = 'Reward'
#        reward_axis.xlabel = 'Time (hours)'
#        reward_axis.ylabel = 'Earnings ($)'
#        reward_axis.grid(True)
        reward_lines = reward_axis.plot(self.reward_data[0, 0], [0], "mx-")
        self.reward_line = reward_lines[0]

        pylab.draw()


    def _render(self):
        """ Calls the render methods.
        """
#        while not self.stopRequest:
#            self.dataLock.acquire()

#        for i, line in enumerate(self.state_lines):
#            ydata = self.state_data[i, :]
#            line.set_ydata(ydata)
#
#        for j, line in enumerate(self.action_lines):
#            ydata = self.action_data[j, :]
#            line.set_ydata(ydata)

        self.reward_line.set_ydata(self.reward_data)

#            self.dataLock.release()

#            time.sleep(0.05)

#        self.stopRequest = False

# EOF -------------------------------------------------------------------------
