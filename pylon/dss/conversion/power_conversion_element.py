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

""" Defines a base class for all power conversion elements """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Instance, Float, Str

from pylon.dss.common.circuit_element import CircuitElement

#------------------------------------------------------------------------------
#  "ConversionElement" class:
#------------------------------------------------------------------------------

class PowerConversionElement(CircuitElement):
    """ Power conversion elements convert power from electrical form to some
    other form, or vice-versa.  Some may temporarily store energy and then give
    it back, as is the case for reactive elements.  Most will have only one
    connection to the power system and, therefore, only one multiphase
    terminal.  The description of the mechanical or thermal side of the power
    conversion is contained within the "Black box" model.  The description may
    be a simple impedance or a complicated set of differential equations
    yielding a current injection equation of the form:

            ITerm(t)  = F(VTerm, [State], t)

    The function F will vary according to the type of simulation being
    performed.  The power conversion element must also be capable of reporting
    the partials matrix when necessary: dF/dV

    In simple cases, this will simply be the primitive y (admittance) matrix;
    that is, the y matrix for this element alone.

    This concept may easily be extended to multi-terminal devices, which would
    allow the representation of complex series elements such as fault current
    limiters.

    """

    # Name of harmonic spectrum for this device.
    spectrum = Str(desc="Harmonic spectrum name")

    # The harmonic spectrum for this device.
    spectrum_obj = Instance(HasTraits, desc="Harmonic spectrum")

    inj_current = Float(0.0)

# EOF -------------------------------------------------------------------------
