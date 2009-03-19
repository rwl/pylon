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

""" Defines the Network class that represents an electric power system
    as a graph of Bus objects connected with Branch objects.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Delegate, \
    Tuple, Array, Bool, Property, Enum, cached_property, on_trait_change

from pylon.bus import Bus
from pylon.branch import Branch
from pylon.generator import Generator
from pylon.load import Load

from pylon.ui.network_view import network_view
from pylon.ui.report_view import pf_report_view, opf_report_view

#------------------------------------------------------------------------------
#  Setup a logger for this module:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Network" class:
#------------------------------------------------------------------------------

class Network(HasTraits):
    """ Defines the Network class that represents an electric power system
        as a graph of Bus objects connected by Branch objects.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Human-readable identifier
    name = String("Network", desc="network name")

    # System base apparent power
    base_mva = Float(100.0, desc="the base apparent power (MVA)")

    #--------------------------------------------------------------------------
    #  Bus objects:
    #--------------------------------------------------------------------------

    # Node of the power system graph
    buses = List(Instance(Bus), desc="graph nodes")

    # Buses that are connected by active branches
    connected_buses = Property(List(Instance(Bus)),
        depends_on=["online_branches"],
        desc="buses that are not islanded")

    # The slack model type
    slack_model = Property(Enum("Distributed", "Single"),
        depends_on=["buses.slack"])

    # Generators --------------------------------------------------------------

    # Convenience list of all generators
    all_generators = Property(List(Instance(Generator)),
        depends_on=["buses.generators"],
        desc="convenience list of all generators")

    # Convenience list of all in service generators attached to
    # non islanded buses
    online_generators = Property(List(Instance(Generator)),
        depends_on=["connected_buses.generators",
                    "connected_buses.generators.online"],
        desc="""convenience list of all in service generators attached "
        to non islanded buses""")

    # Loads -------------------------------------------------------------------

    # Convenience list of all loads
    all_loads = Property(List(Instance(Load)), depends_on=["buses.loads"],
        desc="convenience list of all loads")

    # Convenience list of all in service loads connected to
    # non islanded buses
    online_loads = Property(
        List(Instance(Load)),
        depends_on=["connected_buses.loads",
                    "connected_buses.loads.online"],
        desc="""convenience list of all in service loads connected to
        non islanded buses""")

    # Shunts ------------------------------------------------------------------

#    shunts = List(Instance(HasTraits))

    # Branches ----------------------------------------------------------------

    # Branch edges.
    branches = List(Instance(Branch), desc="branch edges")

    # Branch edges that are in service.
    online_branches = Property(List(Instance(Branch)),
        depends_on=["branches.online"],
        desc="a convenient list of all in service branches")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    # A default view:
    traits_view = network_view

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    @on_trait_change("buses.slack")
    def manage_slack_bus(self, obj, name, old, new):
        """ Ensures that there is never any more than one slack bus.
        """
        if new and self.traits_inited():
            for bus in self.buses:
                if (bus is not obj) and (bus.slack is True):
                    bus.slack = False


    def _buses_changed(self, new):
        """ Handles the bus list being set.
        """
        self.branches = [e for e in self.branches if \
                         (e.source_bus in new) or (e.target_bus in new)]

        # Set the new list of all buses in the network for each branch.
        for branch in self.branches:
            branch.buses = new


    def _buses_items_changed(self, event):
        """ Handles addition and removal of buses. Ensures no dangling
            branches by removing connected to a removed bus.

            Also, maintains each branch's list of buses in the network.
        """

        # Filter out any branches connected to a removed bus.
        for v in event.removed:
            self.branches = [e for e in self.branches if not e.source_bus == v]
            self.branches = [e for e in self.branches if not e.target_bus == v]

        # Set the list of buses in the network for each branch.
        for branch in self.branches:
            branch.buses = self.buses


    def _branches_changed(self, new):
        """ Handles the list of branches changing. Checks that the source
            and target buses for each branch are present in the network.

            Sets the list of buses in the network for each branch also.
        """
        for branch in new:
            # Sanity check on the presence of source/target bus in network.
            if branch.source_bus not in self.buses:
                raise ValueError, "Source bus [%s] for branch [%s] not " \
                    "present in network." % (branch.source_bus, branch)
            if branch.target_bus not in self.buses:
                raise ValueError, "Target bus [%s] for branch [%s] not " \
                    "present in network." % (branch.target_bus, branch)

            # Set the list of buses in the network.
            branch.buses = self.buses


    def _branches_items_changed(self, event):
        """ Handles the addition and removal of branches.

            Set the list of buses in the network for each new branch.
        """
        for branch in event.added:
            # Sanity check on the presence of source/target bus in network.
            if branch.source_bus not in self.buses:
                raise ValueError, "Source bus [%s] for branch [%s] not " \
                    "present in network." % (branch.source_bus, branch)
            if branch.target_bus not in self.buses:
                raise ValueError, "Target bus [%s] for branch [%s] not " \
                    "present in network." % (branch.target_bus, branch)

            # Set the list of buses in the network.
            branch.buses = self.buses

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

    def _get_connected_buses(self):
        """ Provides a list of buses that are not islanded.

            TODO: Possibly use admittance matrix values.
        """

        # This list is in a very different order to the list of all buses
#        non_islanded = []
#        for e in self.online_branches:
#            # Ensure the bus has not already been added (Could use a set)
#            if e.source_bus not in non_islanded:
#                non_islanded.append(e.source_bus)
#            if e.target_bus not in non_islanded:
#                non_islanded.append(e.target_bus)

        if len(self.buses) <= 1:
            return self.buses

        # This is a very slow way, but it returns a list in the same
        # order as the list of all buses and this is useful for
        # testing against MATPOWER and PSAT
        non_islanded = []
        for v in self.buses:
            for e in self.online_branches:
                if e.source_bus == v or e.target_bus == v:
                    if v not in non_islanded:
                        non_islanded.append(v)

        return non_islanded


    def _get_slack_model(self):
        """ Indicates the current slack bus model.
        """
        slackers = [v for v in self.buses if v.slack == True]

        if len(slackers) == 0:
            return "Distributed"
        elif len(slackers) == 1:
            return "Single"

    # Generator property getters ----------------------------------------------

    def _get_all_generators(self):
        """ Property getter """

        return [g for v in self.buses for g in v.generators]


    def _get_online_generators(self):
        """ Provides a convenient list of all generators that are
            connected to non islanded buses.
        """
        buses = self.connected_buses
        return [g for v in buses for g in v.generators if g.online]

    # Load property getters ---------------------------------------------------

    def _get_all_loads(self):
        """ Property getter.
        """
        return [l for v in self.buses for l in v.loads]


    def _get_online_loads(self):
        """ Property getter.
        """
        buses = self.connected_buses
        return [l for v in buses for l in v.loads if l.online]

    #--------------------------------------------------------------------------
    #  Branch property getters:
    #--------------------------------------------------------------------------


    def _get_online_branches(self):
        """ Property getter.
        """
        return [e for e in self.branches if e.online]

#------------------------------------------------------------------------------
#  "NetworkReport" class:
#------------------------------------------------------------------------------

class NetworkReport(HasTraits):
    """ Defines a statistical report of a network.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Network being reported.
    network = Instance(Network, desc="reported network", allow_none=False)

    #--------------------------------------------------------------------------
    #  Delegate trait definitions:
    #--------------------------------------------------------------------------

    # System bus nodes.
    buses = Delegate("network")

    # Connected system buses.
    connected_buses = Delegate("network")

    # All system generators.
    all_generators = Delegate("network")

    # On generators.
    online_generators = Delegate("network")

    # All system loads.
    all_loads = Delegate("network")

    # On loads.
    online_loads = Delegate("network")

    # Branch edges.
    branches = Delegate("network")

    # Active branches.
    online_branches = Delegate("network")

    #--------------------------------------------------------------------------
    #  Property trait definitions:
    #--------------------------------------------------------------------------

    # The total number of buses
    n_buses = Property(Int, depends_on=["buses"],
        desc="total number of buses", label="Buses")

    # The total number of non-islanded buses
    n_connected_buses = Property(Int, depends_on=["connected_buses"],
        desc="total number of non islanded buses")

    # The total number of generators
    n_generators = Property(Int, depends_on=["all_generators"],
        desc="total number of generators", label="Generators")

    # The total number of generators in service
    n_online_generators = Property(Int,
        depends_on=["online_generators"])

    committed_generators = Property(List(Instance(Generator)),
        depends_on=["all_generators.p"])

    n_committed_generators = Property(Int, depends_on=["committed_generators"],
        label="Committed Gens")

    # The total number of all loads
    n_loads = Property(Int, depends_on=["all_loads"], label="Loads")

    # The total number of loads in service
    n_online_loads = Property(Int, depends_on=["online_loads"])

    fixed = Property(List(Instance(Load)), depends_on=["all_loads"],
        desc="Fixed loads")
    n_fixed = Property(Int, depends_on=["fixed"])

    despatchable = Property(List(Instance(Load)),
        depends_on=["all_generators"], desc="negative generators")
    n_despatchable = Property(Int, depends_on=["despatchable"])

#    n_shunts = Property(Int, depends_on=["shunts"])

    n_branches = Property(Int, depends_on=["branches"])

    n_online_branches = Property(Int, depends_on=["online_branches"])

    # Branches operating as transformers.
    transformers = Property(List(Instance(Branch)), depends_on=["branches"])

    n_transformers = Property(Int, depends_on=["transformers"])

    # Inter-ties --------------------------------------------------------------

#    inter_ties = List(Instance(HasTraits))
#    n_inter_ties = Property(Int, depends_on=["inter_ties"])

    # Areas -------------------------------------------------------------------

#    areas = List(Instance(HasTraits))
#    n_areas = Property(Int, depends_on=["areas"])

    #--------------------------------------------------------------------------
    #  Quantity property traits:
    #--------------------------------------------------------------------------

    # Total system generation capacity.
    total_gen_capacity = Property(Float, depends_on=["all_generators.p"])

    # Total capacity of online generation.
    online_capacity = Property(Float, depends_on=["online_generators.p"])

    # Total capacity of despatched generation.
    generation_actual = Property(Float,
                                 depends_on=["all_generators.p_despatch"])

    # Total system load.
    load = Property(Float, depends_on=["all_loads.p"])

    # Total capacity of fixed system load.
    fixed_load = Property(Float, depends_on=["fixed.p"])

    # Total capacity of despatchable loads.
    despatchable_load = Property(Float, depends_on=["despatchable.p"])

    # Total system shunt injection.
#    shunt_injection = Property(Float, depends_on=["shunts"])

    # Total system losses.
    losses = Property(Float, depends_on=["branches.p_losses"])

    # Total branch charging injections.
    branch_charging = Property(Float, depends_on=["branches"])

    # Total inter-tie flow.
#    inter_tie_flow = Property(Float, depends_on=["inter_ties"])

    # Minimum and maximum bus voltages.
    min_voltage_amplitude = Property(Float, depends_on=["buses.v_amplitude"])
    max_voltage_amplitude = Property(Float, depends_on=["buses.v_amplitude"])
    min_voltage_phase = Property(Float, depends_on=["buses.v_phase"])
    max_voltage_phase = Property(Float, depends_on=["buses.v_phase"])

    # Minimum and maximum bus Lagrangian multipliers.
    min_p_lambda = Property(Float, depends_on=["buses.p_lambda"])
    max_p_pambda = Property(Float, depends_on=["buses.p_lambda"])
    min_q_lambda = Property(Float, depends_on=["buses.q_lambda"])
    max_q_lambda = Property(Float, depends_on=["buses.q_lambda"])

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    # Power flow results view.
    pf_view = pf_report_view

    # Optimal power flow results view.
    opf_view = opf_report_view

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network, **traits):
        """ Initialises a NetworkReport instance.
        """
        assert isinstance(network, Network)

        self.network = network
        super(NetworkReport, self).__init__(network=network, **traits)

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

    def _get_n_buses(self):
        """ Property getter for the total number of buses.
        """
        return len(self.buses)


    def _get_n_connected_buses(self):
        """ Property getter for the number of connected buses.
        """
        return len(self.connected_buses)


    def _get_n_generators(self):
        """ Property getter for the total number of generators.
        """
        return len(self.all_generators)


    def _get_n_online_generators(self):
        """ Property getter for the number of active generators.
        """
        return len(self.online_generators)


    def _get_committed_generators(self):
        """ Property getter for the list of generators that have
            been despatched.
        """
        return [g for g in self.all_generators if g.p > 0.0]


    def _get_n_committed_generators(self):
        """ Property getter for the number of committed generators.
        """
        return len(self.committed_generators)


    def _get_n_loads(self):
        """ Property getter for the total number of loads.
        """
        return len(self.all_loads)


    def _get_n_online_loads(self):
        """ Property getter for the number of active loads.
        """
        return len(self.online_loads)


    def _get_fixed(self):
        """ Property getter for the list of fixed loads.
        """
        return self.all_loads


    def _get_n_fixed(self):
        """ Property getter for the total number of fixed loads.
        """
        return len(self.fixed)


    def _get_despatchable(self):
        """ Property getter for the list of generators with negative output.
        """
        return [g for g in self.all_generators if g.p < 0.0]


    def _get_n_despatchable(self):
        """ Property getter for the number of despatchable loads.
        """
        return len(self.despatchable)

#    def _get_n_shunts(self):
#        """ Property getter for the total number of shunts.
#        """
#        return len(self.shunts)

    #--------------------------------------------------------------------------
    #  Branch property getters:
    #--------------------------------------------------------------------------

    def _get_n_branches(self):
        """ Property getter for the total number of branches.
        """
        return len(self.branches)


    def _get_n_online_branches(self):
        """ Property getter for the total number of active branches.
        """
        return len(self.online_branches)


    def _get_transformers(self):
        """ Property getter for the list of branches operating as transformers.
        """
        return [e for e in self.branches if e.mode == "Transformer"]


    def _get_n_transformers(self):
        """ Property getter for the total number of transformers.
        """
        return len(self.transformers)

    #--------------------------------------------------------------------------
    #  Inter-tie property getters:
    #--------------------------------------------------------------------------

#    def _get_n_inter_ties(self):
#        """ Property getter for the total number of inter-ties.
#        """
#        return len(self.inter_ties)

    #--------------------------------------------------------------------------
    #  Area property getters:
    #--------------------------------------------------------------------------

#    def _get_n_areas(self):
#        """ Property getter for the total number of areas.
#        """
#        return len(self.areas)

    #--------------------------------------------------------------------------
    #  "How much?" property getters:
    #--------------------------------------------------------------------------

    def _get_total_gen_capacity(self):
        """ Property getter for the total generation capacity.
        """
        base_mva = self.network.base_mva
        p = sum([g.p for g in self.all_generators])
        q = sum([g.q for g in self.all_generators])

        return complex(p * base_mva, q * base_mva)


    def _get_online_capacity(self):
        """ Property getter for the total online generation capacity.
        """
        p = sum([g.p for g in self.online_generators])
        q = sum([g.q for g in self.online_generators])

        return complex(p, q)


    def _get_generation_actual(self):
        """ Property getter for the total despatched generation.
        """
        p = sum([g.p_despatch for g in self.all_generators])
        q = sum([g.q for g in self.all_generators])

        return complex(p, q)


    def _get_load(self):
        """ Property getter for the total system load.
        """
        p = sum([l.p for l in self.all_loads])
        q = sum([l.q for l in self.all_loads])

        return complex(p, q)


    def _get_fixed_load(self):
        """ Property getter for the total fixed system load.
        """
        p = sum([l.p for l in self.fixed])
        q = sum([l.q for l in self.fixed])

        return complex(p, q)


    def _get_despatchable_load(self):
        """ Property getter for the total volume of despatchable load.
        """
        p = sum([l.p for l in self.despatchable])
        q = sum([l.q for l in self.despatchable])

        return complex(p, q)


#    def _get_shunt_injection(self):
#        """ Property getter for the total system shunt injection.
#        """
#        return 0.0 + 0.0j # FIXME: Implement shunts


    def _get_losses(self):
        """ Property getter for the total system losses.
        """
        p = sum([e.p_losses for e in self.branches])
        q = sum([e.q_losses for e in self.branches])

        return complex(p, q)


    def _get_branch_charging(self):
        """ Property getter for the total branch charging injections.
        """
        return 0.0 + 0.0j # FIXME: Calculate branch charging injections


#    def _get_total_inter_tie_flow(self):
#        """ Property getter for the total inter-tie flow.
#        """
#        return 0.0 + 0.0j # FIXME: Implement inter-ties


    def _get_min_voltage_amplitude(self):
        """ Property getter for the minimum bus voltage amplitude.
        """
        if self.buses:
#            l.index(min(l))
            return min([bus.v_amplitude for bus in self.buses])
        else:
            return 0.0


    def _get_max_voltage_amplitude(self):
        """ Property getter for the maximum bus voltage amplitude.
        """
        if self.buses:
            return max([bus.v_amplitude for bus in self.buses])
        else:
            return 0.0



    def _get_min_voltage_phase(self):
        """ Property getter for the minimum bus voltage phase angle.
        """
        if self.buses:
            return min([bus.v_phase for bus in self.buses])
        else:
            return 0.0


    def _get_max_voltage_phase(self):
        """ Property getter for the maximum bus voltage phase angle.
        """
        if self.buses:
            return max([bus.v_phase for bus in self.buses])
        else:
            return 0.0


    def _get_min_p_lambda(self):
        """ Property getter.
        """
        if self.buses:
            return min([v.p_lambda for v in self.buses])
        else:
            return 0.0


    def _get_max_p_lambda(self):
        """ Property getter.
        """
        if self.buses:
            return max([v.p_lambda for v in self.buses])
        else:
            return 0.0


    def _get_min_q_lambda(self):
        """ Property getter.
        """
        if self.buses:
            return min([v.q_lambda for v in self.buses])
        else:
            return 0.0


    def _get_max_q_lambda(self):
        """ Property getter.
        """
        if self.buses:
            return max([v.q_lambda for v in self.buses])
        else:
            return 0.0

#------------------------------------------------------------------------------
#  "AreaRegion" class:
#------------------------------------------------------------------------------

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
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    n = Network()
    v1 = Bus()
    v2 = Bus()
    n.buses=[v1, v2]
#    e1 = Branch(source_bus=v1, target_bus=v2)
#    n.branches=[e1]


#    import pickle
    import cPickle as pickle
    from tempfile import gettempdir
    from os.path import join
#    from pylon.readwrite.api import read_matpower
#
#    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
##    data_file = "/home/rwl/python/aes/matpower_3.2/case30.m"
#    n = read_matpower(data_file)
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
