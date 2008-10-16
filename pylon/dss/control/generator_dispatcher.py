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
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Bool

from pylon.dss.common.circuit_element import CircuitElement
from pylon.dss.delivery.api import PowerDeliveryElement

from pylon.dss.conversion.api import Generator

from control_element import ControlElement

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
    element = Instance(CircuitElement, allow_none=False)

    # Number of the terminal of the circuit element to which the GenDispatcher
    # control is connected. 1 or 2, typically.  Default is 1. Make sure you
    # have the direction on the power matching the sign of kWLimit.
    terminal = Int(1, desc="Connected terminal")

    # kW Limit for the monitored element. The generators are dispatched to hold
    # the power in band.the object class.
    kw_limit = Float(8000.0, desc="kW Limit for the monitored element")

    # Bandwidth (kW) of the dead band around the target limit. No dispatch
    # changes are attempted if the power in the monitored terminal stays within
    # this band.
    kw_band = Float(
        100.0, desc="Bandwidth (kW) of the dead band around the target limit."
    )

    # Max kvar to be delivered through the element.  Uses same dead band as kW.
    kvar_limit = Float(0.0, desc="Max kVar through the element")

    # Array list of generators to be dispatched.  If not specified, all
    # generators in the circuit are assumed dispatchable.
    gen_list = List(Instance(Generator), desc="generators to be dispatched")

    # Array of proportional weights corresponding to each generator in the
    # gen_list. The needed kW to get back to center band is dispatched to each
    # generator according to these weights. Default is to set all weights to
    # 1.0.
    weights = List(
        Float, [1.0],
        desc="proportional weights corresponding to each generator"
    )

# EOF -------------------------------------------------------------------------
