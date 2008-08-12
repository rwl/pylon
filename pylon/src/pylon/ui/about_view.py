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

""" About Pylon view """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.ui.api import View, Group, Label
from enthought.pyface.image_resource import ImageResource

#-------------------------------------------------------------------------------
#  About Pylon "View" instance:
#-------------------------------------------------------------------------------

credits_label = \
"""
Pylon's power flow and OPF routines are largely derived from the excellent
MATPOWER project by Ray D. Zimmerman, Carlos E. Murillo-Sanchez and
Deqiang (David) Gan.

See http://www.pserc.cornell.edu/matpower/ for further details.
"""

license_label = \
"""
Copyright (C) 2007 Richard W. Lincoln

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 dated June, 1991.

This software is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
"""

contact_label = """
Institute for Energy and Environment
Department of Electronic and Electrical Engineering
The University of Strathclyde
Royal College Building
204 George Street
Glasgow G1 1XW

Tel.\t+44 (0)141 548 4840
Fax\t+44 (0)141 548 4872

Email:\trichard.lincoln@eee.strath.ac.uk
Web:\thttp://www.eee.strath.ac.uk
"""

about_view = View(
    Group(Label(license_label), label="License"),
    Group(Label(contact_label), label="Contact"),
    Group(Label(credits_label), label="Credits"),
    title="About", buttons=["OK"],
    icon=ImageResource("frame.ico")
)

# EOF -------------------------------------------------------------------------
