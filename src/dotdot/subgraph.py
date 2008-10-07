#------------------------------------------------------------------------------
#  Copyright (C) 2007 Richard W. Lincoln
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 dated June, 1991.
#
#  This software is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

#  Generated from Attributes.ecore on Wed 27/08/2008 at 09:14

"""
subgraphempty

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Any


#------------------------------------------------------------------------------
#  "Subgraph" class:
#------------------------------------------------------------------------------

class Subgraph(HasTraits):
    """
    subgraphempty

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Rank
#constraints on the nodes in a subgraph.
#					If <html:span class="val">same</html:span>, all nodes are placed on the same rank.
#					If <html:span class="val">min</html:span>, all nodes are placed on the minimum rank.
#					If <html:span class="val">source</html:span>, all nodes are placed on the minimum rank, and
#					the only nodes on the minimum rank belong to some subgraph whose
#					rank attribute is "source" or "min".
#					Analogous criteria hold for <html:a rel="attr">rank</html:a>=<html:span class="val">max</html:span> and <html:a rel="attr">rank</html:a>=<html:span class="val">sink</html:span>.
#					(Note: the
#					minimum rank is topmost or leftmost, and the maximum rank is bottommost
#					or rightmost.)
#				</html:p>
#			attributerank##targetNamespace
#    rank = Any


    #--------------------------------------------------------------------------
    #  Private interface:
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------



#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Subgraph().configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
