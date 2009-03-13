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

""" This module is responsible for modeling the energy consumers and the system
    load as curves and associated curve data. Special circumstances that may
    affect the load, such as seasons and daytypes, are also included here.

    This information is used by Load Forecasting and Load Management.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Instance, Bool, Range, Enum

from enthought.traits.ui.api \
    import View, Group, Item, VGroup, HGroup

from iec61970.Wires \
    import EnergyConsumer

from iec61970.Core \
    import IdentifiedObject, RegularIntervalSchedule

from iec61970.Domain \
    import CurrentFlow

#------------------------------------------------------------------------------
#  "EnergyArea" class:
#------------------------------------------------------------------------------

class EnergyArea(IdentifiedObject):
    """ The class describes an area having energy production or consumption.
        The class is the basis for further specialization.
    """
    pass

#------------------------------------------------------------------------------
#  "LoadArea" class:
#------------------------------------------------------------------------------

class LoadArea(EnergyArea):
    """ The class is the root or first level in a hierarchical structure for
        grouping of loads for the purpose of load flow load scaling.
    """

    # The SubLoadAreas in the LoadArea.
    SubLoadAreas = List(Instance("SubLoadArea"))#, minlen=1)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, sub_load_areas, **traits):
#        """ Initialises a new SubLoadArea instance.
#        """
#        self.SubLoadAreas = sub_load_areas
#        super(LoadArea, self).__init__(**traits)

#------------------------------------------------------------------------------
#  "SubLoadArea" class:
#------------------------------------------------------------------------------

class SubLoadArea(EnergyArea):
    """ The class is the second level in a hierarchical structure for grouping
        of loads for the purpose of load flow load scaling.
    """

    # The LoadArea where the SubLoadArea belongs.
    LoadArea = Instance(LoadArea, allow_none=False)

    # The Loadgroups in the SubLoadArea.
    LoadGroups = List(Instance("LoadGroup"),# minlen=1,
        desc="load groups in the SubLoadArea")

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, load_area, **traits):
        """ Initialises a new SubLoadArea instance.
        """
        self.LoadArea = load_area
        super(SubLoadArea, self).__init__(**traits)

#------------------------------------------------------------------------------
#  "SeasonDayTypeSchedule" class:
#------------------------------------------------------------------------------

class SeasonDayTypeSchedule(RegularIntervalSchedule):
    """ The schedule specialize RegularIntervalSchedule with type curve data
        for a specific type of day and season. This means that curves of this
        type cover a 24 hour period.
    """
    pass

    # Load demand models can be based on seasons.
#    Season = Instance(Season)

    # Load demand models can be based on day type.
#    DayType = Instance(DayType)

#------------------------------------------------------------------------------
#  "ConformLoadSchedule" class:
#------------------------------------------------------------------------------

class ConformLoadSchedule(SeasonDayTypeSchedule):
    """ A curve of load  versus time (X-axis) showing the active power values
        (Y1-axis) and reactive power (Y2-axis) for each unit of the period
        covered. This curve represents a typical pattern of load over the time
        period for a given day type and season.
    """

#    LoadDataSets = List(Instance(LoadDataSet))

    # The ConformLoadGroup where the ConformLoadSchedule belongs.
    ConformLoadGroup = Instance("ConformLoadGroup", allow_none=False,
        desc="where the ConformLoadSchedule belongs")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(VGroup(["name", "description", "startTime",
                               "value1Multiplier", "value1Unit",
                               "value2Multiplier", "value2Unit",
                               "timeStep", "endTime"],
                       Group(Item("TimePoints", show_label=False,
                                  height=100),
                             label="Time Points", show_border=True),
                       Item("ConformLoadGroup", show_label=False)),
                       id="iec61970.LoadModel.ConformLoadSchedule",
                       title="Conform Load Schedule", resizable=True,
                       buttons=["Help", "OK", "Cancel"])

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, conform_load_group, **traits):
        """ Initialises a new ConformLoadSchedule instance.
        """
        self.ConformLoadGroup = conform_load_group
        self.value1Multiplier = "k"
        self.value1Unit = "W"
        self.value2Multiplier = "k"
        self.value2Unit = "VAr"
        super(ConformLoadSchedule, self).__init__(**traits)

#------------------------------------------------------------------------------
#  "LoadGroup" class:
#------------------------------------------------------------------------------

class LoadGroup(IdentifiedObject):
    """ The class is the third level in a hierarchical structure for grouping
        of loads for the purpose of load flow load scaling.
    """

    # The SubLoadArea where the load group belongs.
    SubLoadArea = Instance(SubLoadArea,# allow_none=False,
        desc="where the load group belongs")

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, sub_load_area, **traits):
#        """ Initialises a new LoadGroup instance.
#        """
#        self.SubLoadArea = sub_load_area
#        super(LoadGroup, self).__init__(**traits)

#------------------------------------------------------------------------------
#  "ConformLoadGroup" class:
#------------------------------------------------------------------------------

class ConformLoadGroup(LoadGroup):
    """ Loads that follows a daily and seasonal load variation pattern.
    """

    # Consumers may be assigned to a load area.
    EnergyConsumers = List(Instance("ConformLoad"), desc="consumers may be "
        "assigned to a load area")

    # The ConformLoadSchedules in the ConformLoadGroup.
    ConformLoadSchedules = List(Instance(ConformLoadSchedule))#, minlen=1)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(VGroup(["name", "description"],
                       Group(Item("SubLoadArea", show_label=False)),
                       Group(Item("ConformLoadSchedules", show_label=False,
                                  height=120),
                             label="Load Schedules", show_border=True),
                       Group(Item("EnergyConsumers", show_label=False,
                                  height=90),
                             label="Energy Consumers", show_border=True)),
                       id="iec61970.LoadModel.ConformLoadGroup",
                       title="Conform Load Group", resizable=True,
                       buttons=["Help", "OK", "Cancel"])

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, sub_load_area, **traits):
#        """ Initialises a new LoadGroup instance.
#        """
#        super(ConformLoadGroup, self).__init__(sub_load_area, **traits)

#------------------------------------------------------------------------------
#  "ConformLoad" class:
#------------------------------------------------------------------------------

class ConformLoad(EnergyConsumer):
    """ ConformLoad represent loads that follow a daily load change pattern
        where the pattern can be used to scale the load with a system load.
    """

    # Consumers may be assigned to a load area.
    LoadGroup = Instance(ConformLoadGroup, desc="load area for consumers")

#------------------------------------------------------------------------------
#  "Load" class:
#------------------------------------------------------------------------------

class Load(ConformLoad):
    """ A generic equivalent for an energy consumer on a transmission or
        distribution voltage level. It may be under load management and also
        has cold load pick up characteristics.
    """

    # The rated individual phase current.
    phaseRatedCurrent = CurrentFlow

    # Permit assignment of loads on a participation factor basis. Given three
    # equivalent loads with factors of 10, 25 and 15, a feeder load of 100 amps
    # could be allocated on the feeder as 20, 50 and 30 amps.
    loadAllocationFactor = Float(desc="assignment of loads on a participation "
        "factor basis")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(VGroup(["name", "description", "customerCount",
                       Group(Item("MemberOf_EquipmentContainer",
                                  show_label=False)),
#                       Group(Item("Terminals", show_label=False, height=80),
#                             label="Terminals", show_border=True),
                       ],
                       Group(Item("LoadGroup", style="simple",
                                  show_label=False))),
                       id="iec61970.LoadModel.Load",
                       title="Load", resizable=True,
                       buttons=["Help", "OK", "Cancel"])

# EOF -------------------------------------------------------------------------
