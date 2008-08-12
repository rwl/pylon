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

"""
For adapting CVXOPT matrices to values that can be edited
by a TabulaEditor.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Property, List, Str

from enthought.traits.ui.tabular_adapter import TabularAdapter

#------------------------------------------------------------------------------
#  "MatrixTabularAdapter" class:
#------------------------------------------------------------------------------

class MatrixTabularAdapter(TabularAdapter):
    """
    For adapting CVXOPT matrices to values that can be edited
    by a TabularEditor.

    """

    # The name of a trait on the object being edited that when changed
    # indicates that the number of columns should be changed
    n_column_trait = Str

    font = "Monospace 10"
    alignment = "right"
    format = "%.2f"
    width = 75

    # The default background color for table rows (even, odd, any rows):
    odd_bg_color = "lightyellow"

    def _n_column_trait_default(self):
        """ Trait initialiser """
        return self.name

    def _columns_default(self):
        """ Trait initialiser """
        self.object.on_trait_change(self._label_columns, self.n_column_trait)

        r, c = getattr(self.object, self.name).size
        return [str(i+1) for i in range(c)]


    def _label_columns(self):
        """ Returns a list of column labels """

        r, c = getattr(self.object, self.name).size
        self.columns = [str(i+1) for i in range(c)]


    def get_item ( self, object, trait, row ):
        """ Returns the value of the *object.trait[row]* item.
        """
        try:
            return getattr(object, trait)[row, :]
        except:
            return None


    def len ( self, object, trait ):
        """ Returns the number of items in the specified *object.trait* list.
        """
        r, c = getattr(object, trait).size
        return r

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from enthought.traits.api import HasTraits, Trait, Int, Instance
    from enthought.traits.ui.api import View, Item, TabularEditor
    from enthought.traits.ui.menu import NoButtons
    from cvxopt.base import matrix, spmatrix, sparse
    from numpy.random import random

    tabular_editor = TabularEditor(adapter=MatrixTabularAdapter())

    class MatrixViewModel(HasTraits):
        rows = Int(40)
        cols = Int(6)
        data = Property(Trait(matrix), depends_on=["rows", "cols"])

        adapter = MatrixTabularAdapter(n_column_trait="cols")

        view = View(
            Item(name="rows", style="simple"), Item(name="cols"),
            Item("data", editor=TabularEditor(adapter=adapter), show_label=False),
            title="Matrix Viewer", width=0.3, height=0.8,
            resizable=True, buttons=NoButtons
        )

        def _get_data(self):
            """ Property getter """
            return matrix(random((self.rows, self.cols)))

#        def _cols_changed(self, new):
#            self.adapter.columns = ["foo"]*new

    demo = MatrixViewModel()

    demo.configure_traits()

# EOF -------------------------------------------------------------------------
