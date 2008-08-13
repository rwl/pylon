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

""" Defines an action that may be selected according to a profile """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Interface, Float

from i_action import IAction

#------------------------------------------------------------------------------
#  "IProfileAction" class:
#------------------------------------------------------------------------------

class IProfileAction(IAction):
    """ Defines an action that may be selected according to a profile """

    # The value used by the profile selector
    value = Float

#    def copy(self):
#        """ Clone an Action """
#
#
#    def nn_coding_size(self):
#        """ Size of an Action's coding (for NN) """
#
#
#    def nn_coding(self):
#        """ Action's coding (for NN) """
#
#
#    def hash_code(self):
#        """ Q-Learning memorising techniques use hashcoding : it is necessary
#        to redefine it for each problem/game
#
#        """
#
#
#    def __eq__(self, o):
#        """ It is up to the programmer to define when two action are declared
#        equal
#
#        """

# EOF -------------------------------------------------------------------------
