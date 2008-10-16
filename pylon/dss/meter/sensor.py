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

""" Defines a sensor """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Int, Enum, List, Float

from pylon.dss.common.circuit_element import CircuitElement

from meter_element import MeterElement

#------------------------------------------------------------------------------
#  "Sensor" class:
#------------------------------------------------------------------------------

class Sensor(MeterElement):
    """ A sensor """

    # Name (Full Object name) of element to which the Sensor is connected.
    element = Instance(CircuitElement)

    # Number of the terminal of the circuit element to which the Sensor is
    # connected. 1 or 2, typically. For Sensoring states, attach Sensor to
    # terminal 1.
    terminal = Int(1)

    # Array of any of { Voltage | Current | kW | kvar } in any order.
    # Quantities being sensed. Scalar magnitudes only.
    modes = List(Enum("Voltage", "Current", "kW", "kVar"))

    # Array of Voltages (kV) measured by the voltage sensor.
    v = List(Float, [7.2])

    # Array of Currents (amps) measured by the current sensor.
    i = List(Float, [0.0])

    # Array of Active power (kW) measurements at the sensor.
    p = List(Float, [0.0])

    # Array of Reactive power (kvar) measurements at the sensor.
    q = List(Float, [0.0])

    # Array of phases being monitored by this sensor. [1, 2, 3] or [2 3 1] or
    # [1], etc.  Corresponds to the order that the measurement arrays will be
    # supplied. Defaults to same number of quantities as phases in the
    # monitored element.
    phases = List(Int, [1, 2, 3], desc="phases being monitored by this sensor")

    # Connection: { wye | delta | LN | LL }. Applies to voltage measurement. If
    # wye or LN, voltage is assumed measured line-neutral; otherwise,
    # line-line.
    conn = Enum("Wye", "Delta", "LN", "LL")

    # Assumed percent error in the measurement.
    pct_error = Float(1.0)

    # Action options: SQERROR: Show square error of the present value of the
    # monitored terminal quantity vs the sensor value. Actual values - convert
    # to per unit in calling program.  Value reported in result window/result
    # variable.
    action = Enum("Square Error", "Actual Values")

# EOF -------------------------------------------------------------------------
