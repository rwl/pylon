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

"""
Every problem where the set of states  can be enumerated might implement
this interface.

It provides methods to compute V*(state), print the values on the display,
allow the programmer to access an individual V*() value.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import HasTraits

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ValueIteration" class:
#------------------------------------------------------------------------------

class ValueIteration(HasTraits):
    """
    Every problem where the set of states  can be enumerated might implement
    this interface.
    
    It provides methods to compute V*(state), print the values on the display,
    allow the programmer to access an individual V*() value.

    """

    def compute_v_star(self, gamma):
        """
        Computes V* for each state, stores the result in a n-dimensionnal
        array, n is the number of State dimensions.
        
        """
        
        raise NotImplementedError()


    def display_v_star(self):
        """
        Display all the values on the screen : it is up to the user to define
        the output format corresponding to its needs (gnuplot...)

        Warning : compute_v_star() must have been called before !
        
        """
        
        raise NotImplementedError()


    def get_v_star(self, e):
        """
        Read V*(State) <br>
        Warning : compute_v_star() must have been called before !
        
        """
        
        raise NotImplementedError()


    def extract_policy(self, gamma):
        """
        Use V* to extract an optimal policy : you must define the output format.
        
        """
        
        raise NotImplementedError()

# EOF -------------------------------------------------------------------------
