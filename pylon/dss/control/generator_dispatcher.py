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

""" Defines a generator controller """

#------------------------------------------------------------------------------
#  "GeneratorDispatcher" class:
#------------------------------------------------------------------------------

class GeneratorDispatcher(ControlElement):
    """ A GenDispatcher is a control element that is connected to a terminal of
    another circuit element and sends dispatch kW signals to a set of
    generators it controls.

    """

    # Full object name of the circuit element, typically a line or transformer,
    # which the control is monitoring. There is no default; must be specified.
    element = None

    # Number of the terminal of the circuit element to which the GenDispatcher
    # control is connected. 1 or 2, typically.  Default is 1. Make sure you
    # have the direction on the power matching the sign of kWLimit.
    terminal = 1

    # kW Limit for the monitored element. The generators are dispatched to hold
    # the power in band.the object class.
    kw_limit = 8000

    # Bandwidth (kW) of the dead band around the target limit. No dispatch
    # changes are attempted if the power in the monitored terminal stays within
    # this band.
    kw_band = 100

    # Max kvar to be delivered through the element.  Uses same dead band as kW.
    kvar_limit = 0

    # Array list of generators to be dispatched.  If not specified, all
    # generators in the circuit are assumed dispatchable.
    gen_list = []

    # Array of proportional weights corresponding to each generator in the
    # gen_list. The needed kW to get back to center band is dispatched to each
    # generator according to these weights. Default is to set all weights to
    # 1.0.
    weights = [1.0]

# EOF -------------------------------------------------------------------------
