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

""" Pylon test suite.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from pylon.test.case_test import CaseTest, BusTest, BranchTest, GeneratorTest, LoadTest

from y_test import BTest, YTest
from dcpf_test import DCPFTest
from acpf_test import NewtonPFTest
from dcopf_test import DCOPFTest
from acopf_test import ACOPFTest
from uc_test import UnitCommitmentTest

from reader_test import MatpowerReaderTest, PSSEReaderTest#, PSATReaderTest

#------------------------------------------------------------------------------
#  "suite" function:
#------------------------------------------------------------------------------

def suite():
    """ Returns the Pylon test suite.
    """
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(CaseTest))
    suite.addTest(unittest.makeSuite(BusTest))
    suite.addTest(unittest.makeSuite(BranchTest))
    suite.addTest(unittest.makeSuite(GeneratorTest))
    suite.addTest(unittest.makeSuite(LoadTest))

    # Routine test cases.
    suite.addTest(unittest.makeSuite(BTest))
    suite.addTest(unittest.makeSuite(YTest))
    suite.addTest(unittest.makeSuite(DCPFTest))
    suite.addTest(unittest.makeSuite(NewtonPFTest))
    suite.addTest(unittest.makeSuite(DCOPFTest))
    suite.addTest(unittest.makeSuite(ACOPFTest))
    suite.addTest(unittest.makeSuite(UnitCommitmentTest))

    # Read/write test cases.
    suite.addTest(unittest.makeSuite(MatpowerReaderTest))
    suite.addTest(unittest.makeSuite(PSSEReaderTest))
#    suite.addTest(unittest.makeSuite(PSATReaderTest))

    return suite


if __name__ == '__main__':
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    unittest.TextTestRunner(verbosity=2).run(suite())

# EOF -------------------------------------------------------------------------
