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

""" Custom traits for Pylon """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    TraitType, List, Tuple, Float, TraitError, Property, Str

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
#  "SparseMatrix" TraitType class:
#------------------------------------------------------------------------------

class SparseMatrix(TraitType):
    """ Define a trait whose value must be a CVXOPT spmatrix """

    def __init__(self, V=[], I=[], J=[], size=(0,0), tc="d", **metadata):
        """ Returns a SparseMatrix trait

        Parameters
        ----------
        V : A number, a sequence of numbers, or a dense matrix.
            This argument specifies the numerical values of the nonzero
            entries.
        I : sequence of integers or integer matrices
            Contains the row and column indices of the nonzero entries. The
            lengths of I and J must be equal. If they are matrices, they are
            treated as lists of indices stored in column-major order
        J : sequence of integers or integer matrices
            Contains the row and column indices of the nonzero entries. The
            lengths of I and J must be equal. If they are matrices, they are
            treated as lists of indices stored in column-major order
        size : a tuple of nonnegative integers
            The row and column dimensions of the matrix. The size argument
            is only needed when creating a matrix with a zero last row or
            last column. If size is not specified, it is determined from I
            and J: the default value for size[0] is max(I)+1 if I is nonempty
            and zero otherwise. The default value for size[1] is max(J)+1 if
            J is nonempty and zero otherwise.
        tc : a string
            The typecode may be "d" or "z", for double and complex matrices,
            respectively. Integer sparse matrices are not implemented.

        Default Value
        -------------
        *value* or ``zeros(min(shape))``, where ``min(shape)`` refers to the
        minimum shape allowed by the matrix. If *size* is not specified, the
        minimum size is (0,0). If *tc* is not specified, typecode is "d".

        Description
        -----------
        A SparseMatrix trait can be thought of as a triplet description of a
        sparse matrix, i.e., a list of entries of the matrix, with for each
        entry the value, row index, and column index. Entries that are not
        included in the list are assumed to be zero.

        """

        try:
            import cvxopt
        except ImportError:
            raise TraitError(
                "Using the SparseMatrix trait type requires the cvxopt "
                "package to be installed."
            )

        from cvxopt.base import spmatrix

        # FIXME: V, I, and J validation

        if tc not in ["d", "z"]:
            raise TraitError("tc should be 'd' or 'z'")

        if not isinstance(size, tuple):
            raise TraitError("size should be a tuple")
        for item in size:
            if not isinstance(item, int):
                raise TraitError("matrix dimensions must be integers")
            if item < 0:
                raise TraitError("matrix dimensions must be nonnegative")

        value = spmatrix(V, I, J, size, tc)

        self.size = size
        self.tc = tc

        super(SparseMatrix, self).__init__(value, **metadata)


    def validate(self, object, name, value):
        """ Validates that the value is a valid spmatrix """

        from cvxopt.base import spmatrix

        # Make sure the value is a spmatrix:
        if not isinstance(value, spmatrix):
            self.error(object, name, value)

        # Make sure the matrix is of the right type:
        if (self.tc is not None) and (value.typecode != self.tc):
            value = spmatrix(value.V, value.I, value.J, tc=value.typecode)

        return value


    def info(self):
        """ Returns descriptive information about the trait """

        tc = size = ""

        if self.size is not None:
            size = " with size %s" % size

        if self.tc is not None:
            # FIXME: better typecode descriptions
            tc = " of %s values"

        return "a sparse matrix%s%s" % (tc, size)


    def get_editor(self, trait=None):
        """ Returns the default UI editor for the trait """

        from enthought.traits.ui.api import TabularEditor

        return TabularEditor(adapter=MatrixTabularAdapter())

    #--------------------------------------------------------------------------
    #  Private interface
    #--------------------------------------------------------------------------

    def get_default_value(self):
        """ Returns the default value constructor for the type (called from
        the trait factory.
        """
        return (7, (self.copy_default_value,
                    (self.validate(None, None, self.default_value), ), None))


    def copy_default_value(self, value):
        """ Returns a copy of the default value (called from the C code on
        first reference to a trait with no current value).
        """

        from cvxopt.base import spmatrix

        return spmatrix(value.V, value.I, value.J)

#------------------------------------------------------------------------------
#  "Matrix" TraitType class:
#------------------------------------------------------------------------------

class Matrix(TraitType):
    """ Defines a trait whose value must be a CVXOPT matrix """

    def __init__(self, value=0, size=(0, 0), tc="i", **metadata):
        """ Returns a Matrix trait

        Parameters
        ----------
        value : CVXOPT matrix
            A default value for the matrix
        size : a tuple
            size is a tuple of length two with the matrix dimensions. The
            number of rows and/or the number of columns can be zero.
        tc : a typecode string
            The possible values are "i", "d" and "z", for integer, real
            (double) and complex matrices, respectively.

        Default Value
        -------------
        *value* or ``zeros(min(shape))``, where ``min(shape)`` refers to the
        minimum shape allowed by the matrix. If *size* is not specified, the
        minimum size is (0,0). If *tc* is not specified, typecode is "i".

        """

        try:
            import cvxopt
        except ImportError:
            raise TraitError(
                "Using the Matrix trait type requires the cvxopt "
                "package to be installed."
            )

        from cvxopt.base import matrix

        if tc not in ["i", "d", "z"]:
            raise TraitError("tc should be 'i', 'd' or 'z'")

        if not isinstance(size, tuple):
            raise TraitError("size should be a tuple")
        if len(size) != 2:
            raise TraitError("size should be a tuple of length two")

        value = matrix(value, size, tc)

        self.size = size
        self.tc = tc

        super(Matrix, self).__init__(value, **metadata)


    def info(self):
        """ Returns descriptive information about the trait """

        tc = size = ""

        if self.size is not None:
            size = " with size %s" % size

        if self.tc is not None:
            # FIXME: better typecode descriptions
            tc = " of %s values"

        return "a matrix%s%s" % (tc, size)


    def get_editor(self, trait=None):
        """ Returns the default UI editor for the trait """

        from enthought.traits.ui.api import TabularEditor

        return TabularEditor(adapter=MatrixTabularAdapter())

    #--------------------------------------------------------------------------
    #  Private interface
    #--------------------------------------------------------------------------

    def get_default_value(self):
        """ Returns the default value constructor for the type (called from
        the trait factory.
        """
        return (7, (self.copy_default_value,
                    (self.validate(None, None, self.default_value), ), None))


    def copy_default_value(self, value):
        """ Returns a copy of the default value (called from the C code on
        first reference to a trait with no current value).
        """

        from cvxopt.base import matrix

        return matrix(value)


    def validate(self, object, name, value):
        """ Validates that the value is a valid matrix """

        from cvxopt.base import matrix

        # Make sure the value is a matrix:
        if not isinstance(value, matrix):
            self.error(object, name, value)

        # Make sure the matrix is of the right type:
        if (self.tc is not None) and (value.typecode != self.tc):
            value = matrix(value, tc=value.typecode)

        return value


    def info(self):
        """ Returns descriptive information about the trait """

        tc = size = ""

        if self.size is not None:
            size = " with size %s" % size

        if self.tc is not None:
            # FIXME: better typecode descriptions
            tc = " of %s values"

        return "a matrix%s%s" % (tc, size)


    def get_editor(self, trait=None):
        """ Returns the default UI editor for the trait """

        from enthought.traits.ui.api import TabularEditor

        return TabularEditor(adapter=MatrixTabularAdapter())

    #--------------------------------------------------------------------------
    #  Private interface
    #--------------------------------------------------------------------------

    def get_default_value(self):
        """ Returns the default value constructor for the type (called from
        the trait factory.
        """
        return (7, (self.copy_default_value,
                    (self.validate(None, None, self.default_value), ), None))


    def copy_default_value(self, value):
        """ Returns a copy of the default value (called from the C code on
        first reference to a trait with no current value).
        """

        from cvxopt.base import matrix

        return matrix(value)

#------------------------------------------------------------------------------
#  "ConvexPiecewise" class:
#------------------------------------------------------------------------------

class ConvexPiecewise(List):
    """
    Defines a trait whose value must be a list of points that define
    a convex piecewise function.

    """

    default_value = [(0.0, 0.0), (1.0, 1.0)]

    def __init__(self, value=None, xmin=None, xmax=None, **metadata):
        """
        Returns a List of convex piecewise points

        Parameters
        ----------
        value : the default value as a list of tuples of two floats


        Default Value
        -------------
        *value* or [(0.0, 0.0), (1.0, 0.1)]

        """

        self.xmin = xmin
        self.xmax = xmax

        if value is None:
            value = self.default_value

        super(ConvexPiecewise, self).__init__(
            trait=Tuple(Float, Float), value=value,
            minlen=2, **metadata
        )


    def validate(self, object, name, value):
        """
        Validates that:
         * the value is a list of two float tuples (x, y)
         * the list has two or more entries
         * each successive x value is greater than the last
         * each successive y value is greater than the last
         * if xmin is not None, that the x value of the first
           point equals xmin
         * if xmax is not None, that the x value of the final
           point equals xmax

        """

        value = super(ConvexPiecewise, self).validate(object, name, value)

        # Validate convexity
        # Coerce (0.0, 0.0) points as these are the default values
        # for points added by the editor
        for i, (xn, yn) in enumerate(value):
            if i != 0:
                # Previous point
                xn_1, yn_1 = value[i-1]
                # Next point
                if i != len(value)-1:
                    xpp, ypp = value[i+1]
                else:
                    xpp = ypp = None

                if xn <= xn_1 or yn <= yn_1:
                    self.error(object, name, value)

        # Enforce x limits by inserting or coercing first
        # and final values
        xmin = self.xmin
        xmax = self.xmax

        if xmin is not None:
            x0, y0 = value[0]
            if x0 > xmin:
                value.insert(0, (xmin, y0))
            elif x0 < xmin:
                # TODO: Linear interpolation
                value[0] = (xmin, y0)
            else:
                pass

        if xmax is not None:
            xn, yn = value[-1]
            if xn < xmax:
                value.append((xmax, yn))
            elif xn > xmax:
                # TODO: Linear interpolation
                value[-1] = (xmax, yn)
            else:
                pass

        return value

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
