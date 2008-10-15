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

""" Defines a base class for DSS objects """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Instance, List, Int, Float, Bool, Str

from pylon.dss.common.collection import Collection

#------------------------------------------------------------------------------
#  "DSSObject" class:
#------------------------------------------------------------------------------

class DSSObject(HasTraits):
    """ A base class for DSS objects """

    # PD, PC, Monitor, CondCode, etc.
    dss_obj_type = Int(0)

    dss_class_name = Str

    parent_class = Instance(Collection)

    # Index into the class collection list
    class_index = Int(0)

    dirty = Bool(False)

    # General purpose Flag for each object - don't assume inited
    flag = Bool(False)

    prop_sequence = List(Float)

# EOF -------------------------------------------------------------------------
