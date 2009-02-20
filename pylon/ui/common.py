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

from enthought.traits.ui.table_column import ObjectColumn

#------------------------------------------------------------------------------
#  "FloatColumn" class:
#------------------------------------------------------------------------------

class FloatColumn(ObjectColumn):
    """ Defines a column that formats floating point numbers.
    """

    format = "%.3f"

#------------------------------------------------------------------------------
#  "InServiceColumn" class:
#------------------------------------------------------------------------------

class InServiceColumn(ObjectColumn):
    """ A specialised column to set the text color differently based upon the
        state of the 'in_service' trait of the object.
    """

    width = 0.08

    horizontal_alignment = "center"

    def get_text_color(self, object):
        return ["light grey", "black"][object.in_service]

#------------------------------------------------------------------------------
#  "InServiceFloatColumn" class:
#------------------------------------------------------------------------------

class InServiceFloatColumn(InServiceColumn):
    """ Defines a column that formats floating point numbers and sets the text
        color differently based upon the state of the 'in_service' trait of the
        object.
    """

    format = "%.3f"

# EOF -------------------------------------------------------------------------
