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

""" Pylon test suite. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from network_test_case import NetworkTest
from bus_test_case import BusTest
from branch_test_case import BranchTest
from generator_test_case import GeneratorTest
from load_test_case import LoadTest

from matrix_test_case import MatrixTest, SparseMatrixTest
from y_test_case import BTest
from dcpf_test_case import DCPFTest
from dcopf_test_case import DCOPFTest
from uc_test_case import UnitCommitmentTest

from reader_test_case import MatpowerReaderTest

#------------------------------------------------------------------------------
#  "suite" function:
#------------------------------------------------------------------------------

def suite():
    """ Returns the pylon test suite. """

    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(NetworkTest))
    suite.addTest(unittest.makeSuite(BusTest))
    suite.addTest(unittest.makeSuite(BranchTest))
    suite.addTest(unittest.makeSuite(GeneratorTest))
    suite.addTest(unittest.makeSuite(LoadTest))

    suite.addTest(unittest.makeSuite(MatrixTest))
    suite.addTest(unittest.makeSuite(SparseMatrixTest))
    suite.addTest(unittest.makeSuite(BTest))
    suite.addTest(unittest.makeSuite(DCPFTest))
    suite.addTest(unittest.makeSuite(DCOPFTest))
    suite.addTest(unittest.makeSuite(UnitCommitmentTest))

    suite.addTest(unittest.makeSuite(MatpowerReaderTest))

    return suite

if __name__ == '__main__':

#    unittest.main()

#    suiteFew = unittest.TestSuite()
#    suiteFew.addTest(testBlogger("testPostNewEntry"))
#    suiteFew.addTest(testBlogger("testDeleteAllEntries"))
#    unittest.TextTestRunner(verbosity=2).run(suiteFew)

    unittest.TextTestRunner(verbosity = 2).run(suite())

# EOF -------------------------------------------------------------------------
