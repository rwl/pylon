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

""" AC OPF matrix visualisation """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Instance, Trait, Button

from enthought.traits.ui.api import \
    Item, Group, View, HGroup, VGroup, DropEditor

from pylon.api import Network
from pylon.routine.api import ACOPFRoutine
from pylon.traits import Matrix, SparseMatrix

#------------------------------------------------------------------------------
#  "ACOPFViewModel" class:
#------------------------------------------------------------------------------

class ACOPFViewModel(HasTraits):
    """ AC OPF matrix visualisation """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The routine providing the matrices
    routine = Instance(ACOPFRoutine, ())

    # The network on which the routine is performed
    network = Instance(Network)

    # A button that fires the routine
    run = Button("Optimal Power Flow")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        VGroup(
            Item(
                name="network", style="readonly",
                editor=DropEditor(klass=Network)
            ),
            Item(name="run", style="simple", show_label=False)
        ),
        id="pylon.routine.dc_opf.view", title="AC OPF Routine",
#        icon=ImageResource("frame.ico", search_path=[IMAGE_LOCATION]),
        resizable=True, style="custom", buttons=["OK"],
        width=.4, height=.4
    )

    #--------------------------------------------------------------------------
    #  "ACOPFViewModel" interface:
    #--------------------------------------------------------------------------

    def _run_fired(self):
        """ Solves the routine and gets the resulting matrices """

        self.routine.solve()

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.filter.api import MATPOWERImporter

    filter = MATPOWERImporter()
    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
#    data_file = "/home/rwl/python/aes/matpower_3.2/case30.m"
    n = filter.parse_file(data_file)

    vm = ACOPFViewModel(network=n)
    vm.configure_traits()

# EOF -------------------------------------------------------------------------
