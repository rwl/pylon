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

""" A player which selects at random """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from random import Random, randint

from enthought.traits.api import HasTraits, implements, Str

from enthought.traits.ui.api import View, Item

from pyqle.selector.i_selector import ISelector

#------------------------------------------------------------------------------
#  "RandomSelector" class:
#------------------------------------------------------------------------------

class RandomSelector(HasTraits):
    """ A player which selects at random """

    implements(ISelector)

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Human readable identifier
    name = Str("Random Selector")

    # The default view
    traits_view = View(Item("name"))

    #--------------------------------------------------------------------------
    #  "ISelector" interface:
    #--------------------------------------------------------------------------

    def choose(self, state, action_list):
        """ Selects an action at random """

        n_action = len(action_list)

        if n_action == 0:
            raise ValueError
        elif n_action == 1:
            return action_list[0]
        else:
            idx = randint(0, n_action-1)
            return action_list[idx]


    def learn(self, starting_state, action, resulting_state, reward):
        """ There is no learning for this algorithm """

        pass


#    def __str__(self):
#        return self.name

# EOF -------------------------------------------------------------------------
