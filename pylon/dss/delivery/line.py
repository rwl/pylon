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

""" Defines the line element """

#------------------------------------------------------------------------------
#  "Line" class:
#------------------------------------------------------------------------------

class Line(PowerDeliveryElement):
    """ Line impedances are specified in per unit length and are multiplied by
    the length when the primitive Y matrix is computed.

    You may specify the impedances of the line either by symmetrical components
    or by R, X, and nodal C matrices  (also per unit length).

    All C's is entered in nano farads.

    The ultimate values are in the matrices.  If you specify matrices, then the
    symmetrical component values are ignored.  However, if you change any of
    the symmetrical component values the matrices will be recomputed.  It is
    assumed you want to use symmetrical component values.  Don't mix data entry
    by matrix and by symmetrical components.

    Note that if you change the number of phases, the matrices are reallocated
    and reinitialized with whatever is currently in the symmetrical component
    data.


    Multi-phase, two-port line or cable.  Pi model.  Power delivery element
    described by its impedance.  Impedances may be specified by symmetrical
    component values or by matrix values.  Alternatively, you may simply refer
    to an existing LineCode object from which the impedance values will be
    copied.  Then you need only specify the length.

    You can define the line impedance at a base frequency directly in a Line
    object definition or you can import the impedance definition from a
    LineCode object. Both of these definitions of impedance are quite similar
    except that the LineCode object can perform Kron reduction.

    If the geometry property is specified all previous definitions are ignored.
    The DSS will compute the impedance matrices from the specified geometry
    each time the frequency changes.

    Whichever definition is the most recent applies, as with nearly all DSS
    functions.

    Note the units property; you can declare any length measurement in whatever
    units you please.  Internally, everything is converted to meters. Just be
    sure to declare the units. Otherwise, they are assumed to be compatible
    with other data or irrelevant.

    """

    # Name of bus for terminal 1. Node order definitions optional.
    bus_1 = None

    # Name of bus for terminal 2.
    bus_2 = None

    # Name of linecode object describing line impedances.
    # If you use a line code, you do not need to specify the impedances here.
    # The line code must have been PREVIOUSLY defined.  The values specified
    # last will prevail over those specified earlier (left-to-right sequence
    # of properties).  If no line code or impedance data are specified, line
    # object defaults to 336 MCM ACSR on 4 ft spacing.
    line_code = ""

    # Length of line. If units do not match the impedance data, specify "units"
    # property.
    length = 1.0

    # No. of phases.  A line has the same number of conductors per terminal as
    # phases.  Neutrals are not explicitly modeled unless declared as a phase
    # and the impedance matrices adjusted accordingly.
    phases = 3

    # Positive-sequence Resistance, ohms per unit length.
    r1 = 0.058

    # Positive-sequence Reactance, ohms per unit length.
    x1 = 0.1206

    # Zero-sequence Resistance, ohms per unit length.
    r0 = 0.1784

    # Zero-sequence Reactance, ohms per unit length.
    x0 = 0.4047

    # Positive-sequence capacitance, nF per unit length.
    c1 = 3.4

    # Zero-sequence capacitance, nF per unit length.
    c0 = 1.6

    # Resistance matrix, lower triangle, ohms per unit length. Order of the
    # matrix is the number of phases. May be used to specify the impedance of
    # any line configuration.  For balanced line models, you may use the
    # standard symmetrical component data definition instead.
    r_matrix = ""

    # Reactance matrix, lower triangle, ohms per unit length. Order of the
    # matrix is the number of phases. May be used to specify the impedance of
    # any line configuration.  For balanced line models, you may use the
    # standard symmetrical component data definition instead.
    x_matrix = ""

    # Nodal Capacitance matrix, lower triangle, nf per unit length.Order of the
    # matrix is the number of phases.  May be used to specify the shunt
    # capacitance of any line configuration.  For balanced line models, you may
    # use the standard symmetrical component data definition instead.
    c_matrix = ""

    # {Y/N | T/F}  Default= No/False.  Designates this line as a switch for
    # graphics and algorithmic purposes.
    # SIDE EFFECT: Sets R1=0.001 X1=0.0. You must reset if you want something
    # different.
    switch = False

    # Carson earth return resistance per unit length used to compute impedance
    # values at base frequency.  For making better frequency adjustments.
    rg = 0.0

    # Carson earth return reactance per unit length used to compute impedance
    # values at base frequency.  For making better frequency adjustments.
    xg = 0.0

    # Earth resitivity used to compute earth correction factor. Overrides Line
    # geometry definition if specified.
    rho = 100

    # Geometry code for LineGeometry Object. Supercedes any previous definition
    # of line impedance. Line constants are computed for each frequency change
    # or rho change. CAUTION: may alter number of phases.
    geometry = ""

    # Length Units = {none | mi|kft|km|m|Ft|in|cm } Default is None - assumes
    # length units match impedance units.
    units = None

# EOF -------------------------------------------------------------------------
