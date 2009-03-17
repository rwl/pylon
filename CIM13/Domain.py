#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" The domain package is a data dictionary of quantities and units that define
    datatypes for attributes (properties) that may be used by any class in any
    other package.

    This package contains the definition of primitive datatypes, including
    units of measure and permissible values. Each datatype contains a value
    attribute and an optional unit of measure, which is specified as a static
    variable initialized to the textual description of the unit of measure. The
    value of the "units" string may be country or customer specific. Typical
    values are given. Permissible values for enumerations are listed in the
    documentation for the attribute using UML constraint syntax inside curly
    braces. Lengths of variable strings are listed in the descriptive text
    where required.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Float, Long, Enum, Tuple, Time, Date

#------------------------------------------------------------------------------
#  Trait definitions:
#------------------------------------------------------------------------------

# Date and time as "yyyy-mm-ddThh:mm:ss.sss", which conforms with ISO 8601.
# UTC time zone is specified as "yyyy-mm-ddThh:mm:ss.sssZ". A local timezone
# relative UTC is specified as "yyyy-mm-ddThh:mm:ss.sss-hh:mm".
# AbsoluteDateTime can be used both for calender time, e.g. 2007-02-07T10:30,
# and for relative time, e.g. 10:30.
#AbsoluteDateTime = Tuple(Time, Date, desc="Date and time as "
#    "'yyyy-mm-ddThh:mm:ss.sss', which conforms with ISO 8601")

# Electrical current (positive flow is out of the ConductingEquipment into the
# ConnectivityNode)
#CurrentFlow = Float(desc="Electrical current (positive flow is out of the "
#    "ConductingEquipment into the ConnectivityNode)")

#Seconds = Float(desc="time, in seconds")

# Units defined for usage in the CIM.
UnitSymbol = Enum("VA", "W", "VAr", "VAh", "Wh", "VArh", "V", "ohm", "A", "F",
    "H", "oC", "s", "min", "deg", "rad", "J", "N", "none", "Hz", "kg", "Pa",
    "m", "m2", "m3", "VVAr", "WHz", "Js", "s1", "kgJ", "Ws",
    desc="units defined for usage in the CIM")

# Unit multipliers defined for the CIM.
UnitMultiplier = Enum("p", "n", "micro", "m", "c", "d", "k", "G", "T", "none",
    desc="unit multipliers defined for the CIM")

# EOF -------------------------------------------------------------------------
