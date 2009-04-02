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
    HasTraits, String, Int, Float, List, Instance, Bool, Range, Enum, \
    on_trait_change

from enthought.traits.ui.api \
    import View, Group, Item, VGroup, HGroup, InstanceEditor

from CIM13.Wires \
    import EnergyConsumer

from CIM13.Core \
    import IdentifiedObject, RegularIntervalSchedule

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
    SubLoadAreas = List(Instance("SubLoadArea"), opposite="LoadArea")

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, sub_load_areas, **traits):
#        """ Initialises a new SubLoadArea instance.
#        """
#        self.SubLoadAreas = sub_load_areas
#        super(LoadArea, self).__init__(**traits)


#    @on_trait_change("SubLoadAreas,SubLoadAreas_items")
#    def _on_subload_areas(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if isinstance(new, TraitListEvent):
#            old = new.removed
#            new = new.added
#
#        for each_old in old:
#            each_old.LoadArea = None
#        for each_new in new:
#            each_new.LoadArea = self

#------------------------------------------------------------------------------
#  "SubLoadArea" class:
#------------------------------------------------------------------------------

class SubLoadArea(EnergyArea):
    """ The class is the second level in a hierarchical structure for grouping
        of loads for the purpose of load flow load scaling.
    """

    # The LoadArea where the SubLoadArea belongs.
    LoadArea = Instance(LoadArea, allow_none=False, opposite="SubLoadAreas")

    # The Loadgroups in the SubLoadArea.
    LoadGroups = List(Instance("LoadGroup"),# minlen=1,
        desc="load groups in the SubLoadArea", opposite="SubLoadArea")

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, load_area, **traits):
#        """ Initialises a new SubLoadArea instance.
#        """
#        self.LoadArea = load_area
#        super(SubLoadArea, self).__init__(**traits)


#    @on_trait_change("LoadArea")
#    def _on_load_area(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if (old is not None) and (self in old.SubLoadAreas):
#            old.SubLoadAreas.remove(self)
#
#        if (old is not None) and (self not in new.SubLoadAreas):
#            new.SubLoadAreas.append(self)
#
#
#    @on_trait_change("LoadGroups,LoadGroups_items")
#    def _on_load_groups(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if isinstance(new, TraitListEvent):
#            old = new.removed
#            new = new.added
#
#        for each_old in old:
#            each_old.SubLoadArea = None
#        for each_new in new:
#            each_new.SubLoadArea = self

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
    ConformLoadGroup = Instance("ConformLoadGroup",# allow_none=False,
        desc="where the ConformLoadSchedule belongs",
        opposite="ConformLoadSchedules")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(VGroup(["name", Item("description", style="custom"),
                               "startTime",
                               "value1Multiplier", "value1Unit",
                               "value2Multiplier", "value2Unit",
                               "timeStep", "endTime"],
                       Group(Item("TimePoints", show_label=False,
                                  height=100),
                             label="Time Points", show_border=True),
                       Item("ConformLoadGroup", show_label=False)),
                       id="CIM13.LoadModel.ConformLoadSchedule",
                       title="Conform Load Schedule", resizable=True,
                       buttons=["Help", "OK", "Cancel"])

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, **traits):
        """ Initialises a new ConformLoadSchedule instance.
        """
        super(ConformLoadSchedule, self).__init__(**traits)

        self.value1Multiplier = "k"
        self.value1Unit = "W"
        self.value2Multiplier = "k"
        self.value2Unit = "VAr"


#    @on_trait_change("ConformLoadGroup")
#    def _on_conform_load_group(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if (old is not None) and (self in old.ConformLoadSchedules):
#            old.ConformLoadSchedules.remove(self)
#
#        if (old is not None) and (self not in new.ConformLoadSchedules):
#            new.ConformLoadSchedules.append(self)

#------------------------------------------------------------------------------
#  "LoadGroup" class:
#------------------------------------------------------------------------------

class LoadGroup(IdentifiedObject):
    """ The class is the third level in a hierarchical structure for grouping
        of loads for the purpose of load flow load scaling.
    """

    # The SubLoadArea where the load group belongs.
    SubLoadArea = Instance(SubLoadArea,# allow_none=False,
        desc="where the load group belongs", opposite="LoadGroups")

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, sub_load_area, **traits):
#        """ Initialises a new LoadGroup instance.
#        """
#        self.SubLoadArea = sub_load_area
#        super(LoadGroup, self).__init__(**traits)


#    @on_trait_change("SubLoadArea")
#    def _on_subload_area(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if (old is not None) and (self in old.LoadGroups):
#            old.LoadGroups.remove(self)
#
#        if (old is not None) and (self not in new.LoadGroups):
#            new.LoadGroups.append(self)

#------------------------------------------------------------------------------
#  "ConformLoadGroup" class:
#------------------------------------------------------------------------------

class ConformLoadGroup(LoadGroup):
    """ Loads that follows a daily and seasonal load variation pattern.
    """

    # Consumers may be assigned to a load area.
    EnergyConsumers = List(Instance("ConformLoad"), desc="consumers may be "
        "assigned to a load area", opposite="LoadGroup")

    # The ConformLoadSchedules in the ConformLoadGroup.
    ConformLoadSchedules = List(Instance(ConformLoadSchedule),
        opposite="ConformLoadGroup")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(VGroup(["name", Item("description", style="custom")],
                       Group(Item("SubLoadArea", show_label=False)),
                       Group(Item("ConformLoadSchedules", show_label=False,
                                  height=120),
                             label="Load Schedules", show_border=True),
                       Group(Item("EnergyConsumers", show_label=False,
                                  height=90),
                             label="Energy Consumers", show_border=True)),
                       id="CIM13.LoadModel.ConformLoadGroup",
                       title="Conform Load Group", resizable=True,
                       buttons=["Help", "OK", "Cancel"])

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, sub_load_area, **traits):
#        """ Initialises a new LoadGroup instance.
#        """
#        super(ConformLoadGroup, self).__init__(sub_load_area, **traits)


#    @on_trait_change("EnergyConsumers,EnergyConsumers_items")
#    def _on_energy_consumers(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if isinstance(new, TraitListEvent):
#            old = new.removed
#            new = new.added
#
#        for each_old in old:
#            each_old.LoadGroup = None
#        for each_new in new:
#            each_new.LoadGroup = self
#
#
#    @on_trait_change("ConformLoadSchedules,ConformLoadSchedules_items")
#    def _on_conform_load_schedules(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if isinstance(new, TraitListEvent):
#            old = new.removed
#            new = new.added
#
#        for each_old in old:
#            each_old.ConformLoadGroup = None
#        for each_new in new:
#            each_new.ConformLoadGroup = self

#------------------------------------------------------------------------------
#  "ConformLoad" class:
#------------------------------------------------------------------------------

class ConformLoad(EnergyConsumer):
    """ ConformLoad represent loads that follow a daily load change pattern
        where the pattern can be used to scale the load with a system load.
    """

    # Consumers may be assigned to a load area.
    LoadGroup = Instance(ConformLoadGroup, desc="load area for consumers",
        opposite="EnergyConsumers")

    _LoadGroups = List(Instance(ConformLoadGroup))


#    @on_trait_change("LoadGroup")
#    def _on_load_group(self, obj, name, old, new):
#        """ Handles the bidirectional relationship.
#        """
#        if (old is not None) and (self in old.EnergyConsumers):
#            old.EnergyConsumers.remove(self)
#
#        if (old is not None) and (self not in new.EnergyConsumers):
#            new.EnergyConsumers.append(self)

#------------------------------------------------------------------------------
#  "Load" class:
#------------------------------------------------------------------------------

class Load(ConformLoad):
    """ A generic equivalent for an energy consumer on a transmission or
        distribution voltage level. It may be under load management and also
        has cold load pick up characteristics.
    """

    # The rated individual phase current.
    phaseRatedCurrent = Float(desc="rated individual phase current")

    # Permit assignment of loads on a participation factor basis. Given three
    # equivalent loads with factors of 10, 25 and 15, a feeder load of 100 amps
    # could be allocated on the feeder as 20, 50 and 30 amps.
    loadAllocationFactor = Float(desc="assignment of loads on a participation "
        "factor basis")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(VGroup(["name", Item("description", style="custom"),
                               "customerCount",
#                       Group(Item("MemberOf_EquipmentContainer",
#                                  show_label=False)),
#                       Group(Item("Terminals", show_label=False, height=80),
#                             label="Terminals", show_border=True),
                       ],
                       Group(Item("LoadGroup", style="simple",
                                  editor=InstanceEditor(name="_LoadGroups",
                                                        editable=True),
                                  show_label=False))),
                       id="CIM13.LoadModel.Load",
                       title="Load", resizable=True,
                       buttons=["Help", "OK", "Cancel"])

# EOF -------------------------------------------------------------------------
