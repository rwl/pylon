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

""" Defines user interface objects common to certain network elements.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Font, Color

from enthought.traits.ui.table_column import ObjectColumn

from enthought.traits.ui.menu import Menu, Action

#------------------------------------------------------------------------------
# For calculating a unique name given a list of existing names.
#------------------------------------------------------------------------------

def make_unique_name(base, existing=[], format="%s_%s"):
    """ Return a name, unique within a context, based on the specified name.

        base: the desired base name of the generated unique name.
        existing: a sequence of the existing names to avoid returning.
        format: a formatting specification for how the name is made unique.
    """
    count = 2
    name = base
    while name in existing:
        name = format % (base, count)
        count += 1

    return name

#------------------------------------------------------------------------------
#  "ContextMenuColumn" class:
#------------------------------------------------------------------------------

class ContextMenuColumn(ObjectColumn):
    """ Defines a column with a context menu that appears when the column is
        right-clicked.
    """

    # Column context menu.
    menu = Menu( Action( name   = 'Edit Properties',
                         action = 'column.configure( object )' ))

    # Text font for this column:
    text_font = Font

    # Cell background color for this column:
    cell_color = Color( 'white' )

    # Cell graph color:
    graph_color = Color( 0xA4D3EE )

    def configure ( self, object ):
        """ Edit properties of the selected object.
        """
        object.edit_traits(kind='livemodal')

#------------------------------------------------------------------------------
#  "FloatColumn" class:
#------------------------------------------------------------------------------

class FloatColumn(ContextMenuColumn):
    """ Defines a column that formats floating point numbers.
    """

    format = "%.3f"

#------------------------------------------------------------------------------
#  "OnlineColumn" class:
#------------------------------------------------------------------------------

class OnlineColumn(ContextMenuColumn):
    """ A specialised column to set the text color differently based upon the
        state of the 'online' trait of the object.
    """

#    width = 0.08

    horizontal_alignment = "center"

    def get_text_color(self, object):
        return ["light grey", "black"][object.online]

#------------------------------------------------------------------------------
#  "OnlineFloatColumn" class:
#------------------------------------------------------------------------------

class OnlineFloatColumn(OnlineColumn):
    """ Defines a column that formats floating point numbers and sets the text
        color differently based upon the state of the 'online' trait of the
        object.
    """
    format = "%.3f"

# EOF -------------------------------------------------------------------------
