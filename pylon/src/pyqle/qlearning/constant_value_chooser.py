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
generated source for ConstantValueChooser

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import Float

# Local imports:
from abstract_value_chooser import AbstractValueChooser

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ConstantValueChooser" class:
#------------------------------------------------------------------------------

class ConstantValueChooser(AbstractValueChooser):
    """
    generated source for ConstantValueChooser

    """
    
    constant_value = Float(0.0)

    def __init__(self, value):
        self.constant_value = value
        super(ConstantValueChooser, self).__init__(constant_value=value)


    def get_value(self):
        return self.constant_value

# EOF -------------------------------------------------------------------------
