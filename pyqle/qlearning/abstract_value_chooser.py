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
When no values are yet stored for a (s,a) couple, the IRewardStore
(or its implemented classes) asks this class for a default value to return.
Values might be constant (@see ConstantValueChooser) or inside an interval 
(@see IntervalValueChooser).

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits

#------------------------------------------------------------------------------
#  "AbstractValueChooser" class:
#------------------------------------------------------------------------------

class AbstractValueChooser(HasTraits):
    """
    When no values are yet stored for a (s,a) couple, the IRewardStore
    (or its implemented classes) asks this class for a default value to return.
    Values might be constant (@see ConstantValueChooser) or inside an interval 
    (@see IntervalValueChooser).

    """

    def get_value(self):
        raise NotImplementedError()

# EOF -------------------------------------------------------------------------
