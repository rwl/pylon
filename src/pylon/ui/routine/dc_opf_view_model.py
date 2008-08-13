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

""" DC OPF matrix visualisation """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Instance, Trait, Button

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, DropEditor, VGroup

from pylon.api import Network
from pylon.routine.api import DCOPFRoutine
from pylon.traits import Matrix, SparseMatrix

#------------------------------------------------------------------------------
#  "DCOPFViewModel" class:
#------------------------------------------------------------------------------

class DCOPFViewModel(HasTraits):
    """ DCOPF matrix visualisation """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The routine providing the matrices
    routine = Instance(DCOPFRoutine)

    # The network on which the routine is performed
    network = Instance(Network)

    # A button that fires the routine
    run = Button("Optimal Power Flow")

    # CVXOPT can optionally make use of the MOSEK solver
    solver = Trait("CVXOPT", {"CVXOPT": None, "MOSEK": "mosek"})

    # The equality and inequality problem constraints combined:
    A_eq = SparseMatrix
    A_ieq = SparseMatrix
    b_eq = Matrix
    b_ieq = Matrix

    # Objective function of the form 0.5 * x'*H*x + c'*x:
    H = SparseMatrix
    c = Matrix

    # The solution:
    x = Matrix

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        HGroup(
            Item(
                name="network", style="readonly",
                editor=DropEditor(klass=Network)
            ),
            Item(name="solver"),
            Item(name="run", style="simple", show_label=False)
        ),
        "_",
        HGroup(
            Item(name="H", width=0.6, label="H"),
            Item(name="c", width=0.1, label="c"),
            Item(name="x", width=0.1, label="x"),
            label="Objective function - 0.5 * x'*H*x + c'*x",
            show_border=True,
            id=".objective_function",
#            layout="split",
        ),
        HGroup(
            Item(name="A_eq", label="A"),
            Item(name="b_eq", label="b", width=0.1),
            label="Equality constraints - A*x = b",
            show_border=True,
            id=".equality_constraints",
#            layout="split"
        ),
        HGroup(
            Item(name="A_ieq", label="G"),
            Item(name="b_ieq", label="h", width=0.1),
            label="Inequality constraints - G*x <= h",
            show_border=True,
            id=".inequality_constraints",
#            layout="split"
        ),
#        dock="tab",
        id="pylon.routine.dc_opf.view",
        title="DC OPF Routine",
#        icon=ImageResource("frame.ico", search_path=[IMAGE_LOCATION]),
        resizable=True,
        style="custom",
        buttons=["OK"],
        width=.8,
        height=.8
    )

    #--------------------------------------------------------------------------
    #  "DCOPFViewModel" interface:
    #--------------------------------------------------------------------------

    def _routine_default(self):
        """ Trait initialiser """

        return DCOPFRoutine(network=self.network)


    def _network_changed(self, new):
        """ Sets the network attribute of the routine """

        self.routine.network = new


    def _solver_changed(self, new):
        """ Sets the solver attribute of the routine """

        print "SOLVER:", self.solver_
        self.routine.solver = self.solver_ # NB Mapped trait


    def _run_fired(self):
        """ Solves the routine and gets the resulting matrices """

        self.routine.solve()

        self.A_eq = self.routine._AA_eq
        self.A_ieq = self.routine._AA_ieq
        self.b_eq = self.routine._bb_eq
        self.b_ieq = self.routine._bb_ieq

        self.H = self.routine._hh
        self.c = self.routine._cc
        self.x = self.routine.x

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.filter.api import MATPOWERImporter

    filter = MATPOWERImporter()
    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
#    data_file = "/home/rwl/python/aes/matpower_3.2/case30.m"
    n = filter.parse_file(data_file)

    print n.buses
    for e in n.branches:
        print e.source_bus, e.target_bus

    vm = DCOPFViewModel(network=n)
    vm.configure_traits(filename="/tmp/dcopf.pkl")

    n = vm.network
    print n.buses
    for e in n.branches:
        print e.source_bus, e.target_bus

# EOF -------------------------------------------------------------------------
