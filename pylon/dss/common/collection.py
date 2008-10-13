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

""" Defines a base class for all DSS collection classes. """

#------------------------------------------------------------------------------
#  "Collection" class:
#------------------------------------------------------------------------------

class Collection:
    """ Base Class for all DSS collection classes.  Keeps track of objects of
    each class, dispatches edits, etc

    """

    n_properties = 0

    property_name = []

    property_help = []

    property_idx_map = {}

    # Maps property to internal command number
    rev_property_idx_map = {}

    element_list = []

    saved = False

# EOF -------------------------------------------------------------------------
