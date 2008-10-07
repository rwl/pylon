#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" Defines the Network class that represents an electric power system as
a graph of Buses connected by Branches.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from numpy import array

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Delegate, \
    Event, Tuple, Button, Array, Bool, Property, Enum, cached_property, \
    on_trait_change

from pylon.bus import Bus
from pylon.branch import Branch
from pylon.generator import Generator
from pylon.load import Load

from pylon.ui.network_view import network_view

# Setup a logger for this module
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Network" class:
#------------------------------------------------------------------------------

class Network(HasTraits):
    """ Defines the Network class that represents an electric power system as
    a graph of Buses connected by Branches.

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Human-readable identifier
    name = String("Untitled", desc="network name")

    # System base apparent power
    mva_base = Float(100.0, desc="the base apparent power (MVA)")

    #--------------------------------------------------------------------------
    #  Bus objects:
    #--------------------------------------------------------------------------

    # Node of the power system graph
    buses = List(Instance(Bus), desc="graph nodes")

    # The total number of buses
    n_buses = Property(
        Int, depends_on=["buses"], desc="total number of buses"
    )

    # Buses that are connected by active branches
    non_islanded_buses = Property(
        List(Instance(Bus)), depends_on=["in_service_branches"],
        desc="buses that are not islanded"

    )

    # The total number of non-islanded buses
    n_non_islanded_buses = Property(
        Int, depends_on=["non_islanded_buses"],
        desc="total number of non islanded buses"

    )

    # All bus names
    bus_names = Property(List(String), depends_on=["buses"])

    # The slack model type
    slack_model = Property(
        Enum("Distributed", "Single"), depends_on=["buses.slack"]
    )

    # Generators --------------------------------------------------------------

    # Convenience list of all generators
    generators = Property(
        List(Generator), depends_on=["buses.generators"],
        desc="convenience list of all generators"
    )

    # The total number of generators
    n_generators = Property(
        Int, depends_on=["generators"], desc="total number of generators"
    )

    # Convenience list of all in service generators attached to
    # non islanded buses
    in_service_generators = Property(
        List(Instance(Generator)),
        depends_on=[
            "non_islanded_buses.generators",
            "non_islanded_buses.generators.in_service"
        ],
        desc="""convenience list of all in service generators attached "
        to non islanded buses"""
    )

    # The total number of generators in service
    n_in_service_generators = Property(
        Int, depends_on=["in_service_generators"],
        desc="total number of active generators"
    )

    # Loads -------------------------------------------------------------------

    # Convenience list of all loads
    loads = Property(
        List(Instance(Load)), depends_on=["buses.loads"],
        desc="convenience list of all loads"
    )

    # The total number of all loads
    n_loads = Property(
        Int, depends_on=["loads"], desc="total number of loads"
    )

    # Convenience list of all in service loads connected to
    # non islanded buses
    in_service_loads = Property(
        List(Instance(Load)),
        depends_on=[
            "non_islanded_buses.loads",
            "non_islanded_buses.loads.in_service"
        ],
        desc="""convenience list of all in service loads connected to
        non islanded buses"""
    )

    # The total number of loads in service
    n_in_service_loads = Property(
        Int, depends_on=["in_service_loads"],
        desc="total number of active loads"
    )

    #--------------------------------------------------------------------------
    #  Branch objects:
    #--------------------------------------------------------------------------

    branches = List(Instance(Branch), desc="edges")

    n_branches = Property(Int, depends_on=["branches"])

    in_service_branches = Property(
        List(Branch), depends_on=["branches.in_service"],
        desc="a convenient list of all in service branches"
    )

    n_in_service_branches = Property(
        Int, depends_on=["in_service_branches"],
        desc="total number of active branches"
    )

    branch_names = Property(List(String), depends_on=["branches"])

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    # A default view:
    traits_view = network_view

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

#    @cached_property
    def _get_n_buses(self):
        """ Property getter """

        return len(self.buses)


#    @cached_property
    def _get_non_islanded_buses(self):
        """ Provides a list of buses that are not islanded
        TODO: Possibly use admittance matrix values

        """

        # This list is in a very different order to the list of all buses
#        non_islanded = []
#        for e in self.in_service_branches:
#            # Ensure the bus has not already been added (Could use a set)
#            if e.source_bus not in non_islanded:
#                non_islanded.append(e.source_bus)
#            if e.target_bus not in non_islanded:
#                non_islanded.append(e.target_bus)

        # This is a very slow way, but it returns a list in the same
        # order as the list of all buses and this is useful for
        # testing against MATPOWER and PSAT
        non_islanded = []
        for v in self.buses:
            for e in self.in_service_branches:
                if e.source_bus == v or e.target_bus == v:
                    if v not in non_islanded:
                        non_islanded.append(v)

        return non_islanded


#    @cached_property
    def _get_n_non_islanded_buses(self):
        """ Property getter """

        return len(self.non_islanded_buses)


#    @cached_property
    def _get_bus_names(self):
        """ Property getter """

        return [bus.name for bus in self.buses]


#    @cached_property
    def _get_slack_model(self):
        """ Indicates the current slack bus model """

        slackers = [v for v in self.buses if v.slack == True]

        if len(slackers) == 0:
            return "Distributed"
        elif len(slackers) == 1:
            return "Single"

    # Generator property getters ----------------------------------------------

#    @cached_property
    def _get_generators(self):
        """ Property getter """

        return [g for v in self.buses for g in v.generators]


#    @cached_property
    def _get_n_generators(self):
        """ Property getter """

        return len(self.generators)


#    @cached_property
    def _get_in_service_generators(self):
        """ Provides a convenient list of all generators that are connected
        to non islanded buses.

        """

        buses = self.non_islanded_buses

        return [g for v in buses for g in v.generators if g.in_service]


#    @cached_property
    def _get_n_in_service_generators(self):
        """ Property getter """

        return len(self.in_service_generators)

    # Load property getters ---------------------------------------------------

#    @cached_property
    def _get_loads(self):
        """ Property getter """

        return [l for v in self.buses for l in v.loads]


#    @cached_property
    def _get_n_loads(self):
        """ Property getter """

        return len(self.loads)


#    @cached_property
    def _get_in_service_loads(self):
        """ Property getter """

        buses = self.non_islanded_buses

        return [l for v in buses for l in v.loads if l.in_service]


#    @cached_property
    def _get_n_in_service_loads(self):
        """ Property getter """

        return len(self.in_service_loads)

    #--------------------------------------------------------------------------
    #  Branch property getters:
    #--------------------------------------------------------------------------

#    @cached_property
    def _get_n_branches(self):
        """ Property getter """

        return len(self.branches)


#    @cached_property
    def _get_in_service_branches(self):
        """ Property getter """

        return [e for e in self.branches if e.in_service]


#    @cached_property
    def _get_n_in_service_branches(self):
        """ Property getter """

        return len(self.in_service_branches)


#    @cached_property
    def _get_branch_names(self):
        """ Property getter """

        return [branch.name for branch in self.branches]

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    @on_trait_change("buses.slack")
    def manage_slack_bus(self, obj, name, old, new):
        """ Ensure that there is never any more than one slack bus """

        if new is True:
            for v in self.buses:
                if v is not obj and v.slack is True:
                    v.slack = False


    def _buses_items_changed(self, event):
        """ Ensure no dangling objects. Remove any other branch components
        connected to a removed bus.

        """

        for v in event.removed:
            self.branches = [e for e in self.branches if not e.source_bus == v]
            self.branches = [e for e in self.branches if not e.target_bus == v]

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------

    def add_branch(self, branch):
        """ Add a Branch instance """

        if len(self.buses) < 2:
            logger.error("For Branch addition two or more buses are requisite")
        elif branch.source_bus not in self.buses:
            raise ValueError, "source bus not present in model"
        elif branch.target_bus not in self.buses:
            raise ValueError, "destination bus not found in model"
        else:
            self.branches.append(branch)

#-------------------------------------------------------------------------------
#  "AreaRegion" class:
#-------------------------------------------------------------------------------

#class AreaRegion(HasTraits):
#    """
#
#    """
#
#    type = Enum("area", "region")
#
#    rating_s = Float(desc="power rate (MVA)")
#
#    p_export = Float(desc="interchange export (> 0 = out) (p.u.)")
#
#    p_tolerance = Float(desc="interchange tolerance (p.u.)")
#
#    p_delta = Float(desc="annual growth rate")

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    n = Network()
    v1 = Bus()
    v2 = Bus()
    n.buses=[v1, v2]
#    e1 = Branch(network=n, source_bus=v1, target_bus=v2)
#    n.branches=[e1]


#    import pickle
    import cPickle as pickle
    from tempfile import gettempdir
    from os.path import join
#    from pylon.filter.api import import_matpower
#
#    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
##    data_file = "/home/rwl/python/aes/matpower_3.2/case30.m"
#    n = import_matpower(data_file)
#
#    n.configure_traits(filename="/tmp/network.pkl")
#
#    print "BEFORE:", n.buses
#    for e in n.branches:
#        print e.source_bus, e.target_bus

    fd_1 = open(join(gettempdir(), "n.pkl"), "wb")
#    pickle.Pickler(fd_1, True).dump(n)
    pickle.dump(n, fd_1)
    fd_1.close()

    fd_2 = open(join(gettempdir(), "n.pkl"), "rb")
#    n2 = pickle.Unpickler(fd_2).load()
    n2 = pickle.load(fd_2)
    fd_2.close()

    n2.configure_traits()

#    print "AFTER:", n2.buses
#    for e in n2.branches:
#        print e.source_bus, e.target_bus

# EOF -------------------------------------------------------------------------
