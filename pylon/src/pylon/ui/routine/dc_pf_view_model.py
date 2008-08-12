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

""" DC power flow matrix visualisation """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Instance, Trait, Button

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, DropEditor, TabularEditor

from cvxopt.base import matrix, spmatrix

from pylon.network import Network
from pylon.routine.api import DCPFRoutine
from pylon.traits import Matrix, SparseMatrix

#------------------------------------------------------------------------------
#  "DCPFViewModel" class:
#------------------------------------------------------------------------------

class DCPFViewModel(HasTraits):
    """ DC power flow matrix visualisation """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The routine providing the matrices
    routine = Instance(DCPFRoutine, ())

    # The network on which the routine is performed
    network = Instance(Network)

    # Branch susceptance matrix
    B = SparseMatrix(desc="Branch susceptance matrix")

    # Branch source bus susceptance matrix
    B_source = SparseMatrix(desc="Branch source bus susceptance matrix")

    # A button that causes the routine to be solved
    run = Button("Power Flow")

    # The default view
    traits_view = View(
        Item(
            name="network", style="readonly",
            editor=DropEditor(klass=Network)
        ),
        Item(name="run", style="simple", show_label=False),
        Item(name="B"),
        Item(name="B_source"),
        id="pylon.routine.dc_pf.view",
#        title="DC Engine",
#        icon=ImageResource("frame.ico", search_path=[IMAGE_LOCATION]),
        resizable=True,
        style="custom",
        buttons=["OK"],
        width=.2, #height = .4
    )

    #--------------------------------------------------------------------------
    #  "DCPFViewModel" interface:
    #--------------------------------------------------------------------------

    def _network_changed(self, new):
        """ Sets the network attribute of the routine """

        self.routine.network = new


    def _run_fired(self):
        """ Solves the routine and gets the resulting matrices """

        self.routine.solve()
        self.B = self.routine.B
        self.B_source = self.routine.B_source

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.filter.api import MATPOWERImporter

    filter = MATPOWERImporter()
    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
#    data_file = "/home/rwl/python/aes/matpower_3.2/case30.m"
    n = filter.parse_file(data_file)

    vm = DCPFViewModel(network=n)
    vm.configure_traits()

# EOF -------------------------------------------------------------------------
