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
generated source for IntervalValueChooser

See qlearning.IDefaultValueChooser#getvalue()

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import Float, Long

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "IntervalValueChooser" class:
#------------------------------------------------------------------------------

class IntervalValueChooser(DefaultValueChooser):
    """
    generated source for IntervalValueChooser
    
    See qlearning.IDefaultValueChooser#getvalue()

    """
    
    serial_version_uid = Long
    
    lower_bound = Float
    
    upper_bound = Float
    
    generator = Instance(Random, ())


    def __init__(self, lb, ub, **traits):
        self.lower_bound = lb
        self.upper_bound = ub
        
        super(IntervalValueChooser, self).__init__(lower_bound=lb,
            upper_bound=ub, **traits)


    def get_value(self):
        return self.generator.next_double() * \
            self.upper_bound - self.lower_bound + self.lowerBound

# EOF -------------------------------------------------------------------------
