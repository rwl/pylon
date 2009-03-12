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

""" Defines IEC 61970 CIM.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Bool, Range, \
    Property, Enum, Any, Delegate, Tuple, Array, Disallow, cached_property

from iec61850 import BaseElement, LNodeContainer

#------------------------------------------------------------------------------
#  "IdentifiedObject" class:
#------------------------------------------------------------------------------

class IdentifiedObject(BaseElement):
    """ This is a root class to provide common naming attributes for all
        classes needing naming attributes.
    """

    # The name is a free text human readable name of the object. It may be non
    # unique and may not correlate to a naming hierarchy.
    name = Str(desc="a free text human readable name of the object")

    # The description is a free human readable text describing or naming the
    # object. It may be non unique and may not correlate to a naming hierarchy.
    description = Str(desc="a free human readable text describing or naming " \
        "the object")

#------------------------------------------------------------------------------
#  "PowerSystemResource" class:
#------------------------------------------------------------------------------

class PowerSystemResource(IdentifiedObject):#, LNodeContainer):
    """ A power system resource can be an item of equipment such as a Switch,
        an EquipmentContainer containing many individual items of equipment
        such as a Substation, or an organisational entity such as Company or
        SubControlArea.  This provides for the nesting of collections of
        PowerSystemResources within other PowerSystemResources. For example,
        a Switch could be a member of a Substation and a Substation could be
        a member of a division of a Company.
    """

#------------------------------------------------------------------------------
#  "Equipment" class:
#------------------------------------------------------------------------------

class Equipment(PowerSystemResource):
    """ The parts of a power system that are physical devices, electronic or
        mechanical.
    """

    # The association is used in the naming hierarchy.
    member_of_equipment_container = Instance(HasTraits,
        desc="used in the naming hierarchy")

#------------------------------------------------------------------------------
#  "ConductingEquipment" class:
#------------------------------------------------------------------------------

class ConductingEquipment(Equipment):
    """ The parts of the power system that are designed to carry current or
        that are conductively connected therewith. ConductingEquipment is
        contained within an EquipmentContainer that may be a Substation, or
        a VoltageLeve or a Bay within a Substation.
    """

    # Describes the phases carried by a conducting equipment.
    phases = Enum()

#------------------------------------------------------------------------------
#  "IEC61970" class:
#------------------------------------------------------------------------------

class IEC61970(HasTraits):
    """ Defines IEC 61970 CIM.
    """

    # This package is responsible for modeling the energy consumers and the
    # system load as curves and associated curve data. Special circumstances
    # that may affect the load, such as seasons and daytypes, are also
    # included here.
    #
    # This information is used by Load Forecasting and Load Management.
    loadmodel = List(Instance(HasTraits), desc="""package is responsible for
        modeling the energy consumers and the system load as curves and
        associated curve data.""")


    generation = List(Instance(HasTraits), desc="""packages that have
        information for Unit Commitment and Economic Dispatch of Hydro and
        Thermal Generating Units, Load Forecasting, Automatic Generation
        Control, and Unit Modeling for Dynamic Training Simulator""")

#------------------------------------------------------------------------------
#  "IEC61970" class:
#------------------------------------------------------------------------------

class IEC61970(HasTraits):


# EOF -------------------------------------------------------------------------
