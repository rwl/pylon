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

from enthought.traits.api import \
    HasTraits, Instance, Trait, Button, Bool, Int, Float, Range, \
    on_trait_change

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, DropEditor, VGroup

from pylon.network import Network, NetworkReport
from pylon.routine.api import DCOPFRoutine
from pylon.traits import Matrix, SparseMatrix

from pylon.ui.report_view import opf_report_view

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

    #--------------------------------------------------------------------------
    #  Algorithm parameters:
    #--------------------------------------------------------------------------

    # Turns the output to the screen on or off.
    show_progress = Bool(True, desc="the output to screen to be on or off")

    # Maximum number of iterations.
    max_iterations = Range(low=2, high=999, value=100, mode="spinner",
                           desc="maximum number of iterations")

    # Absolute accuracy.
    absolute_tol = Float(1e-7, desc="absolute accuracy")

    # Relative accuracy.
    relative_tol = Float(1e-6, desc="relative accuracy")

    # Tolerance for feasibility conditions.
    feasibility_tol = Float(1e-7, desc="tolerance for feasibility conditions")

    # Number of iterative refinement steps when solving KKT equations.
    refinement = Range(low=2, high=999, value=100, mode="spinner",
                       desc="number of iterative refinement steps when "
                       "solving KKT equations")

    #--------------------------------------------------------------------------
    #  Constraint and objective function traits:
    #--------------------------------------------------------------------------

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
            VGroup(
                Item(
                    name="network", style="readonly",
                    editor=DropEditor(klass=Network)
                ),
                Item(name="solver"),
                Item(name="run", style="simple", show_label=False)
            ),
            VGroup(["show_progress", "max_iterations", "refinement"]),
            VGroup(["absolute_tol", "relative_tol", "feasibility_tol"],
                   style="simple")
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

        self.routine.solver = self.solver_ # N.B. Mapped trait.


    @on_trait_change("show_progress,max_iterations,refinement")
    def map_to_model(self, obj, name, old, new):
        """ Maps view model attributes to the model.
        """
        if hasattr(self.routine, name):
            setattr(self.routine, name, new)
        else:
            raise ValueError("%s" % name)


    @on_trait_change("run")
    def solve(self):
        """ Solves the routine and gets the resulting matrices """

        solution = self.routine.solve()

        self.A_eq = self.routine._AA_eq
        self.A_ieq = self.routine._AA_ieq
        self.b_eq = self.routine._bb_eq
        self.b_ieq = self.routine._bb_ieq

        self.H = self.routine._hh
        self.c = self.routine._cc
        self.x = self.routine.x

#        report = NetworkReport(self.network)
#        report.edit_traits(view=opf_report_view, kind="livemodal")
#        del report

        return solution

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.readwrite.api import read_matpower

    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
#    data_file = "/home/rwl/python/aes/matpower_3.2/case30.m"
    n = read_matpower(data_file)

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
