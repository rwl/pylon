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

""" Defines CIM RDF/XML file parsing tests.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from os.path import join, dirname

from CIM13 import Model

from pylon.readwrite.cim_reader import CIMReader, read_cim

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

CIM_DATA_FILE = join(dirname(__file__), "data", "9bus.xml")

#------------------------------------------------------------------------------
#  "CIMReaderTest" class:
#------------------------------------------------------------------------------

class CIMReaderTest(unittest.TestCase):
    """ Tests parsing of CIM RDF/XML files.
    """

    def test_9bus(self):
        """ Test parsing of of CIM RDF/XML file.
        """

        model = read_cim(CIM_DATA_FILE)

        self.assertEqual( len(model.Contains), 9 )

if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
