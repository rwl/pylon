#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Defines a base class for control elements """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Bool, Str

from pylon.dss.common.circuit_element import CircuitElement

from pylon.dss.common.bus import Bus

#------------------------------------------------------------------------------
#  "ControlElement" class:
#------------------------------------------------------------------------------

class ControlElement(CircuitElement):
    """ Base for control classes """

    element_name = Str

    element_terminal = Int(1)

    controlled_bus_name = Str

    controlled_bus = Instance(Bus)

    monitored_variable = Str

    monitored_var_index = Int(1)

    time_delay = Float(0.0)

    dbl_trace_param = Float(0.0)

# EOF -------------------------------------------------------------------------
