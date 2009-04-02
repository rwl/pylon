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

""" Defines the core PowerSystemResource and ConductingEquipment entities
    shared by all applications plus common collections of those entities.
    Not all applications require all the Core entities.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from itertools import count

from enthought.traits.api import \
    HasTraits, Str, Int, Float, List, Instance, Bool, Property, Enum, Tuple, \
    on_trait_change

from enthought.traits.ui.api \
    import View, Group, Item, VGroup, HGroup, InstanceEditor

from CIM13 import Root

from CIM13.Domain \
    import UnitSymbol, UnitMultiplier

PhaseCode = Enum("ABCN", "ABC", "ABN", "ACN", "BCN", "AB", "AC", "BC",
                  "AN", "BN", "CN", "A", "B", "C", "N",)

CurveStyle = Enum("straightLineYValues", "rampYValue", "constantYValue",
    "formula")

#------------------------------------------------------------------------------
#  "IdentifiedObject" class:
#------------------------------------------------------------------------------

class IdentifiedObject(Root):
    """ This is a root class to provide common naming attributes for all
        classes needing naming attributes.
    """

    # The name is a free text human readable name of the object. It may be non
    # unique and may not correlate to a naming hierarchy.
#    name = Str(desc="a free text human readable name of the object")
    name = Property(Str)
    _name = None

    # The description is a free human readable text describing or naming the
    # object. It may be non unique and may not correlate to a naming hierarchy.
    description = Str(desc="a free human readable text describing or naming " \
        "the object")

    #--------------------------------------------------------------------------
    #  Guarantee unique name:
    #--------------------------------------------------------------------------

    _name_ids = count(0)

    def _name_default(self):
        """ Trait initialiser.
        """
        return self._generate_name()


    def _get_name(self):
        """ Returns the name, which is generated if it has not been already.
        """
        if self._name is None:
            self._name = self._generate_name()
        return self._name


    def _set_name(self, newname):
        """ Change name to newname. Uniqueness is not guaranteed anymore.
        """
        self._name = newname


    def _generate_name(self):
        """ Return a unique name for this object.
        """
        return "%s-%i" % (self.__class__.__name__,  self._name_ids.next())


    def __repr__(self):
        """ The default representation of a named object is its name.
        """
        return "<%s '%s'>" % (self.__class__.__name__, self.name)

#------------------------------------------------------------------------------
#  "Terminal" class:
#------------------------------------------------------------------------------

class Terminal(IdentifiedObject):
    """ An electrical connection point to a piece of conducting equipment.
        Terminals are connected at physical connection points called
        "connectivity nodes".
    """

    # ConductingEquipment has 1 or 2 terminals that may be connected to other
    # ConductingEquipment terminals via ConnectivityNodes
    ConductingEquipment = Instance("CIM13.Core.ConductngEquipment",
        allow_none=False, opposite="Terminals")

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, conducting_equipment, **traits):
#        """ Initialises a new Terminal instance.
#        """
#        self.ConductingEquipment = conducting_equipment
#        super(Terminal, self).__init__(**traits)

#    @on_trait_change("ConductingEquipment")
#    def _on_conducting_equipment(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if (old is not None) and (self in old.Terminals):
#            old.Terminals.remove(self)
#
#        if (old is not None) and (self not in new.Terminals):
#            new.Terminals.append(self)

#------------------------------------------------------------------------------
#  "PowerSystemResource" class:
#------------------------------------------------------------------------------

class PowerSystemResource(IdentifiedObject):
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
#    MemberOf_EquipmentContainer = Instance(HasTraits,
#        desc="used in the naming hierarchy")

#------------------------------------------------------------------------------
#  "ConductingEquipment" class:
#------------------------------------------------------------------------------

class ConductingEquipment(Equipment):
    """ The parts of the power system that are designed to carry current or
        that are conductively connected therewith. ConductingEquipment is
        contained within an EquipmentContainer that may be a Substation, or
        a VoltageLeve or a Bay within a Substation.
    """

    # ConductingEquipment has 1 or 2 terminals that may be connected to other
    # ConductingEquipment terminals via ConnectivityNodes
    Terminals = List(Instance(Terminal), maxlen=2,# minlen=1,
        desc="1 or 2 terminals that may be connected to other "
        "ConductingEquipment terminals via ConnectivityNodes",
        opposite="ConductingEquipment")

    # Describes the phases carried by a conducting equipment.
    phases = PhaseCode

#    def _Terminals_default(self):
#        """ Trait initialiser.
#        """
#        return [Terminal(conducting_equipment=self),
#                Terminal(conducting_equipment=self)]

#    @on_trait_change("Terminals,Terminals_items")
#    def _on_terminals(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if isinstance(new, TraitListEvent):
#            old = new.removed
#            new = new.added
#
#        for each_old in old:
#            each_old.ConductingEquipment = None
#        for each_new in new:
#            each_new.ConductingEquipment = self

##    @on_trait_change("Terminals_items")
##    def OnTerminalsItems(self, event):
##        """ Handles addition and removal of items.
##        """
##        for each_removed in event.removed:
##            each_removed.ConductingEquipment = None
##        for each_added in event.added:
##            each_added.ConductingEquipment = self

#------------------------------------------------------------------------------
#  "RegularTimePoint" class:
#------------------------------------------------------------------------------

class RegularTimePoint(Root):
    """ TimePoints for a schedule where the time between the points is
        constant.
    """

    # A RegularTimePoint belongs to a RegularIntervalSchedule.
    IntervalSchedule = Instance("RegularIntervalSchedule",
        opposite="TimePoints")#, allow_none=False)

    # The position of the RegularTimePoint in the sequence. Note that time
    # points don't have to be sequential, i.e. time points may be omitted.
    # The actual time for a RegularTimePoint is computed by multiplying the
    # RegularIntervalSchedule.timeStep with the RegularTimePoint.sequenceNumber
    # and add the BasicIntervalSchedule.startTime.
    sequenceNumber = Int(desc="position of the RegularTimePoint in the "
        "sequence")

    # The first value at the time. The meaning of the value is defined by the
    # class inhering the RegularIntervalSchedule.
    value1 = Float(desc="first value at the time")

    # The second value at the time. The meaning of the value is defined by the
    # class inhering the RegularIntervalSchedule.
    value2 = Float(desc="second value at the time")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(["sequenceNumber", "value1", "value2",
                        "IntervalSchedule"],
                       id="CIM13.Core.RegularTimePoint",
                       title="Time Point", resizable=True,
                       buttons=["Help", "OK", "Cancel"])

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, interval_schedule, **traits):
#        """ Initialises a new RegularIntervalSchedule instance.
#        """
#        self.IntervalSchedule = interval_schedule
#        super(RegularTimePoint, self).__init__(**traits)

#    @on_trait_change("IntervalSchedule")
#    def _on_interval_schedule(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if (old is not None) and (self in old.TimePoints):
#            old.TimePoints.remove(self)
#
#        if (old is not None) and (self not in new.TimePoints):
#            new.TimePoints.append(self)

#------------------------------------------------------------------------------
#  "BasicIntervalSchedule" class:
#------------------------------------------------------------------------------

class BasicIntervalSchedule(IdentifiedObject):
    """ Schedule of values at points in time.
    """

    # The time for the first time point.
    startTime = Str

    # Value1 units of measure.
    value1Unit = UnitSymbol

    # Multiplier for value1.
    value1Multiplier = UnitMultiplier

    # Value2 units of measure.
    value2Unit = UnitSymbol

    # Multiplier for value2.
    value2Multiplier = UnitMultiplier

#------------------------------------------------------------------------------
#  "RegularIntervalSchedule" class:
#------------------------------------------------------------------------------

class RegularIntervalSchedule(BasicIntervalSchedule):
    """ The schedule has TimePoints where the time between them is constant.
    """

    # The point data values that define a curve.
    TimePoints = List(Instance(RegularTimePoint),# minlen=1,
        desc="point data values that define a curve",
        opposite="IntervalSchedule")

    timeStep = Float

    endTime = Str

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, time_points, **traits):
#        """ Initialises a new RegularIntervalSchedule instance.
#        """
#        self.TimePoints = time_points
#        super(RegularIntervalSchedule, self).__init__(**traits)


    def _TimePoints_default(self):
        """ Trait initialiser.
        """
        return [RegularTimePoint(IntervalSchedule=self)]


#    @on_trait_change("TimePoints,TimePoints_items")
#    def _on_time_points(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if isinstance(new, TraitListEvent):
#            old = new.removed
#            new = new.added
#
#        for each_old in old:
#            each_old.IntervalSchedule = None
#        for each_new in new:
#            each_new.IntervalSchedule = self

#------------------------------------------------------------------------------
#  "Curve" class:
#------------------------------------------------------------------------------

class Curve(IdentifiedObject):
    """ Relationship between an independent variable (X-axis) and one or
        two dependent variables (Y1-axis and Y2-axis). Curves can also serve
        as schedules.
    """

    # The point data values that define a curve
    CurveScheduleDatas = List(Instance("CurveData"),
        desc="point data values that define a curve", opposite="CurveSchedule")

    # The style or shape of the curve.
    curveStyle = CurveStyle

    # Multiplier for X-axis.
    xMultiplier = UnitMultiplier

    # The X-axis units of measure.
    xUnit = UnitSymbol

    # Multiplier for Y1-axis.
    y1Multiplier = UnitMultiplier

    # The Y1-axis units of measure.
    y1Unit = UnitSymbol

    # Multiplier for Y1-axis.
    y1Multiplier = UnitMultiplier

    # The Y1-axis units of measure.
    y1Unit = UnitSymbol


#    @on_trait_change("CurveScheduleDatas,CurveScheduleDatas_items")
#    def _on_time_points(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if isinstance(new, TraitListEvent):
#            old = new.removed
#            new = new.added
#
#        for each_old in old:
#            each_old.CurveSchedule = None
#        for each_new in new:
#            each_new.CurveSchedule = self

#------------------------------------------------------------------------------
#  "CurveData" class:
#------------------------------------------------------------------------------

class CurveData(Root):
    """ Data point values for defining a curve or schedule.
    """

    # The point data values that define a curve.
    CurveSchedule = Instance(Curve, opposite="CurveScheduleDatas")

    # The data value of the X-axis variable,  depending on the X-axis units
    xvalue = Float(desc="data value of the X-axis variable")

    # The data value of the  first Y-axis variable, depending on the Y-axis
    # units.
    y1value = Float(desc="data value of the  first Y-axis variable")

    # The data value of the second Y-axis variable (if present), depending on
    # the Y-axis units
    y2value = Float(desc="data value of the second Y-axis variable")


#    @on_trait_change("CurveSchedule")
#    def _on_curve_schedule(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if (old is not None) and (self in old.CurveScheduleDatas):
#            old.CurveScheduleDatas.remove(self)
#
#        if (old is not None) and (self not in new.CurveScheduleDatas):
#            new.CurveScheduleDatas.append(self)

# EOF -------------------------------------------------------------------------
