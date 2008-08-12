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
Memorising eligibility traces.

See algorithms.AbstractQLambdaSelector

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import \
    HasTraits, Any, List, Long

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Eligibles" class:
#------------------------------------------------------------------------------

class Eligibles(HasTraits):
    """
    Memorising eligibility traces.
    
    See algorithms.AbstractQLambdaSelector

    """
    
    serial_version_uid = Long
    
    map = Dict


    def increment(self, s, a):
        map = {}
        dv = map[ActionStatePair(a, s)]
        value = float()
        if dv is None:
            value = 0
        else:
            value = dv.doubleValue()
        map.put(ActionStatePair(a, s), Double(1 + value))


    def get(self, s, a, us=None):
        """
        Read eligibility value
        
        """
        
        if un is not None:
            dv = map[ActionStatePair(a, s)]
        else:
            dv = map[us]
        
        value = float()
        if dv is None:
            value = 0
        else:
            value = dv.doubleValue()
        return value


    def set(self, s, a, value):
        """
        Store eligibility value
        
        """
        
        map.put(ActionStatePair(a, s), Double(value))


    def put(self, us, value):
        """
        Store eligibility value
        
        """
        
        map.put(us, Double(value))


    def get_iterator(self):
        """
        Iterator on (state,action) pairs
        
        """
        
        keys = map.keySet()
        return keys.iterator()

# EOF -------------------------------------------------------------------------
