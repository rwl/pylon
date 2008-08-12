#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" The basic Q-Learning algorithm.

http://www.cs.ualberta.ca/~sutton/book/ebook/node65.html
Sutton & Barto p 149 Q-Learning

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import HasTraits, Instance, implements

from pyqle.qlearning.reward_memoriser import RewardMemoriser
from i_selector import ISelector
from memory_selector import MemorySelector

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "QLearningSelector" class:
#------------------------------------------------------------------------------

class QLearningSelector(MemorySelector):
    """ The basic Q-Learning algorithm.

    http://www.cs.ualberta.ca/~sutton/book/ebook/node65.html
    Sutton & Barto p 149 Q-Learning

    """

    implements(ISelector)

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    memory = Instance(RewardMemoriser)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, default_value_chooser=None, **traits):
        if default_value_chooser is not None:
            memory = RewardMemoriser(default_value_chooser)
        else:
            memory = RewardMemoriser()

        self.memory = memory

        super(QLearningSelector, self).__init__(memory=memory, **traits)


#    def show_histogram(self):
#        """
#        When <code>states</code> and <code>actions</code> are memorized,
#        one can enumerate them and build histograms showing the distribution of
#        Q(s,a) values
#
#        """
#        self.memory.make_histogram()
#        self.memory.display_histogram()

# EOF -------------------------------------------------------------------------
