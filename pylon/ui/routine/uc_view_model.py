#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Unit commitment visualisation. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Instance, Trait, Button

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, DropEditor, TabularEditor

from pylon.network import Network
from pylon.routine.api import UnitCommitmentRoutine
from pylon.traits import Matrix, SparseMatrix

#------------------------------------------------------------------------------
#  "UnitCommitmentViewModel" class:
#------------------------------------------------------------------------------

class UnitCommitmentViewModel(HasTraits):
    """ Unit commitment visualisation. """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The routine being visualised
    routine = Instance(UnitCommitmentRoutine, ())

    # The network on which the routine is performed
    network = Instance(Network)

    # A button that fires the routine
    run = Button("Solve")

    # The default view
    traits_view = View(
        Item(
            name="network", style="readonly",
            editor=DropEditor(klass=Network)
        ),
        Item(name="run", style="simple", show_label=False),
        id="pylon.routine.uc.view",
#        icon=ImageResource("frame.ico", search_path=[IMAGE_LOCATION]),
        resizable=True, style="custom",
        buttons=["OK"], width=.2
    )

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    vm = UnitCommitmentViewModel(network=Network())
    vm.configure_traits()

# EOF -------------------------------------------------------------------------
