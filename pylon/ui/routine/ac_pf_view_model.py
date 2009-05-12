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

""" AC Power Flow matrix visualisation """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Instance, Bool, Int, Float, Button, on_trait_change

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, DropEditor, HGroup

from pylon.network import Network, NetworkReport
from pylon.routine.api import NewtonPFRoutine
from pylon.traits import Matrix, SparseMatrix

from pylon.ui.report_view import pf_report_view

#------------------------------------------------------------------------------
#  "ACPFViewModel" class:
#------------------------------------------------------------------------------

class ACPFViewModel(HasTraits):
    """ AC Power Flow matrix visualisation """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The routine providing the matrices
    routine = Instance(NewtonPFRoutine)

    # The network on which the routine is performed
    network = Instance(Network)

    # A button that fires the routine
    run = Button("Power Flow")

    # Flag indicating if the solution converged:
    converged = Bool(False)

    # Convergence tolerance
    tolerance = Float(1e-08)

    # Maximum number of iterations:
    iter_max = Int(10)

    # The initial bus voltages:
    v = Matrix

    # Sparse admittance matrix:
    Y = SparseMatrix

    # Apparent power supply at each node:
    s_surplus = Matrix

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Item(
            name="network", style="readonly",
            editor=DropEditor(klass=Network)
        ),
        Item(name="run", style="simple", show_label=False),
        HGroup(
            Item(name="converged", style="readonly"),
            Item(name="tolerance", style="simple")
        ),
        Item(
            name="maximum_iterations",
            label="Max iterations",
            style="simple"
        ),
        Item(name="v"),
        Item(name="Y"),
        Item(name="s_surplus"),
        id="pylon.ui.routine.ac_pf_view_model",
#        title="AC Power Flow",
#        icon=ImageResource("frame.ico"),
        resizable=True, buttons=["OK"],
        width=.4, height=.4
    )

    def _routine_default(self):
        """ Trait initialiser. """

        return NewtonPFRoutine(self.network)


    def _tolerance_changed(self, new):
        """ Delegates the tolerance to the routine """

        self.routine.tolerance = new


    def _iter_max_changed(self, new):
        """ Delegates the maximum number of iterations to the routine """

        self.routine.iter_max = new


    @on_trait_change("run")
    def solve(self):
        """ Solves the routine and gets the resulting matrices """

        self.routine.solve()

        self.converged = self.routine.converged
        self.v = self.routine.v
        self.Y = self.routine.Y
        self.s_surplus = self.routine.s_surplus

        report = NetworkReport(self.network)
        report.edit_traits(view=pf_report_view, kind="livemodal")
        del report

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.readwrite.api import read_matpower

    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
#    data_file = "/home/rwl/python/aes/matpower_3.2/case30.m"
    n = read_matpower(data_file)

    vm = ACPFViewModel(network=n)
    vm.configure_traits()

# EOF -------------------------------------------------------------------------
