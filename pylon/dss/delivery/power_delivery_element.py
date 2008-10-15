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

""" Defines a base class for power delivery elements """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Float, Int

from pylon.dss.common.circuit_element import CircuitElement

#------------------------------------------------------------------------------
#  "DeliveryElement" class:
#------------------------------------------------------------------------------

class PowerDeliveryElement(CircuitElement):
    """ Power delivery elements usually consist of two or more multiphase
    terminals.  Their basic function is to transport energy from one point to
    another.  On the power system, the most common power delivery elements are
    lines and transformers.  Thus, they generally have more than one terminal
    (capacitors and reactors can be an exception when shunt-connected rather
    than series-connected).  Power delivery elements are standard electrical
    elements generally completely defined in the rms steady state by their
    impedances.

    """

    # Normal rated current.
    norm_amps = Float(400.0)

    # Maximum current.
    emerg_amps = Float(600.0, desc="Maximum current")

    # No. of failures per year.
    fault_rate = Float(0.1, desc="Failures per year")

    # Percent of failures that become permanent.
    pct_perm = Float(20.0, desc="Failures that become permanent")

    # Hours to repair.
    repair = Int(3, desc="Hours to repair")

# EOF -------------------------------------------------------------------------
