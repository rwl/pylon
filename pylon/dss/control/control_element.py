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
#  "ControlElement" class:
#------------------------------------------------------------------------------

class ControlElement(CircuitElement):
    """ Base for control classes """

    element_name = ""

    element_terminal = 1

    controlled_bus_name = ""

    controlled_bus = None

    monitored_variable = ""

    monitored_var_index = 1

    time_delay = 0

    dbl_trace_param = 0.0

# EOF -------------------------------------------------------------------------
