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
    HasTraits, Instance, Array, Trait, Bool, Int, Float, Button

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, DropEditor

from pylon.api import Network
from pylon.routine.api import ACPFRoutine
from pylon.traits import Matrix, SparseMatrix

#------------------------------------------------------------------------------
#  "ACPFViewModel" class:
#------------------------------------------------------------------------------

class ACPFViewModel(HasTraits):
    """ AC Power Flow matrix visualisation """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The routine providing the matrices
    routine = Instance(ACPFRoutine, ())

    # The network on which the routine is performed
    network = Instance(Network)

    # A button that fires the routine
    run = Button("Power Flow")

    # Flag indicating if the solution converged:
    converged = Bool(False)

    # Convergence tolerance
    tolerance = Float(1e-08)

    # Maximum number of iterations:
    maximum_iterations = Int(10)

    # The initial bus voltages:
    initial_voltage = Matrix

    # Sparse admittance matrix:
    admittance = SparseMatrix

    # Apparent power supply at each node:
    apparent_supply = Matrix

    # Apparent power demand at each node:
    apparent_demand = Matrix

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Item(
            name="network", style="readonly",
            editor=DropEditor(klass=Network)
        ),
        Item(name="run", style="simple", show_label=False),
        Item(name="converged", style="readonly"),
        Item(name="tolerance", style="simple"),
        Item(
            name="maximum_iterations",
            label="Max iterations",
            style="simple"
        ),
        Item(name="initial_voltage"),
        Item(name="admittance"),
        Item(name="apparent_supply"),
        Item(name="apparent_demand"),
        id="pylon.ui.routine.ac_pf_view_model",
#        title="AC Power Flow",
#        icon=ImageResource("frame.ico"),
        resizable=True, buttons=["OK"],
        width=.4, height=.4
    )

    def _tolerance_changed(self, new):
        """ Delegates the tolerance to the routine """

        self.routine.tolerance = new


    def _maximum_iterations_changed(self, new):
        """ Delegates the maximum number of iterations to the routine """

        self.routine.maximum_iterations = new


    def _run_fired(self):
        """ Solves the routine and gets the resulting matrices """

        self.routine.solve()

        self.converged = self.routine.converged
        self.initial_voltage = self.routine.initial_voltage
        self.admittance = self.routine.admittance
        self.apparent_supply = self.routine.apparent_supply
        self.apparent_demand = self.routine.apparent_demand

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.filter.api import MATPOWERImporter

    filter = MATPOWERImporter()
    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
#    data_file = "/home/rwl/python/aes/matpower_3.2/case30.m"
    n = filter.parse_file(data_file)

    vm = ACPFViewModel(network=n)
    vm.configure_traits()

# EOF -------------------------------------------------------------------------
