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

""" Defines a transformer controller """

#------------------------------------------------------------------------------
#  "RegControl" class:
#------------------------------------------------------------------------------

class RegControl:
    """ A RegControl is a control element that is connected to a terminal of
    another circuit element that must be a transformer.

    """

    # Name of Transformer element to which the RegControl is connected. Do not
    # specify the full object name; "Transformer" is assumed for the object
    # class.
    transformer = None

    # Number of the winding of the transformer element that the RegControl is
    # monitoring. 1 or 2, typically.  Side Effect: Sets TAPWINDING property to
    # the same winding.
    winding = 1

    # Voltage regulator setting, in VOLTS, for the winding being controlled.
    # Multiplying this value times the ptratio should yield the voltage across
    # the WINDING of the controlled transformer.
    v_reg = 120.0

    # Bandwidth in VOLTS for the controlled bus (see help for ptratio property)
    band = 3.0

    # Ratio of the PT that converts the controlled winding voltage to the
    # regulator voltage. If the winding is Wye, the line-to-neutral voltage is
    # used.  Else, the line-to-line voltage is used.
    pt_ratio = 60.0

    # Rating, in Amperes, of the primary CT rating for converting the line amps
    # to control amps.The typical default secondary ampere rating is 5 Amps.
    ct_prim = 300

    # R setting on the line drop compensator in the regulator, expressed in
    # VOLTS.
    r = 0.0

    # X setting on the line drop compensator in the regulator, expressed in
    # VOLTS.
    x = 0.0

    # Name of a bus in the system to use as the controlled bus instead of the
    # bus to which the winding is connected or the R and X line drop
    # compensator settings.  Do not specify this value if you wish to use the
    # line drop compensator settings.  Default is null string. Assumes the base
    # voltage for this bus is the same as the transformer winding base
    # specified above. Note: This bus WILL BE CREATED by the regulator control
    # upon SOLVE if not defined by some other device.
    bus = None

    # Time delay, in seconds, from when the voltage goes out of band to when
    # the tap changing begins. This is used to determine which regulator
    # control will act first. You may specify any floating point number to
    # achieve a model of whatever condition is necessary.
    delay = 15

    # Indicates whether or not the regulator can be switched to regulate in the
    # reverse direction. Default is No.Typically applies only to line
    # regulators and not to LTC on a substation transformer.
    reversible = False

    # Voltage setting in volts for operation in the reverse direction.
    rev_v_reg = 120

    # Bandwidth for operating in the reverse direction.
    rev_band = 3

    # R line drop compensator setting for reverse direction.
    rev_r = 0.0

    # X line drop compensator setting for reverse direction.
    rev_x = 0.0

    # Delay in sec between tap changes. This is how long it takes between
    # changes after the first change.
    tap_delay = 2

    # Turn this on to capture the progress of the regulator model for each
    # control iteration.  Creates a separate file for each RegControl named
    # "REG_name.CSV".
    debug_trace = False

    # Maximum allowable tap change per control iteration in STATIC control
    # mode. Set this to 1 to better approximate actual control action. Set this
    # to 0 to fix the tap in the current position.
    max_tap_change = 16

    # The time delay is adjusted inversely proportional to the amount the
    # voltage is outside the band down to 10%.
    inverse_time = False

    # Winding containing the actual taps, if different than the WINDING
    # property. Defaults to the same winding as specified by the WINDING
    # property.
    tap_winding = 1

# EOF -------------------------------------------------------------------------
