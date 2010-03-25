#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Pylon test suite.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from pylon.test.case_test import CaseTest, BusTest, BranchTest
from pylon.test.generator_test import GeneratorTest, OfferBidToPWLTest

from dcpf_test import DCPFTest
from acpf_test import NewtonPFTest#, FastDecoupledTest
from dcopf_test import PiecewiseLinearDCOPFTest#, DCOPFTest
from acopf_test import ACOPFTest
from opf_test import OPFTest, DCOPFSolverTest, PIPSSolverTest, OPFModelTest
from uc_test import UnitCommitmentTest

from reader_test import MatpowerReaderTest#, PSSEReaderTest, PSATReaderTest

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
    suite.addTest(unittest.makeSuite(OfferBidToPWLTest))

    # Solver test cases.
#    suite.addTest(unittest.makeSuite(DCPFTest))
#    suite.addTest(unittest.makeSuite(NewtonPFTest))
    suite.addTest(unittest.makeSuite(PiecewiseLinearDCOPFTest))
#    suite.addTest(unittest.makeSuite(OPFTest))
#    suite.addTest(unittest.makeSuite(DCOPFSolverTest))
#    suite.addTest(unittest.makeSuite(PIPSSolverTest))
#    suite.addTest(unittest.makeSuite(OPFModelTest))

    # Read/write test cases.
    suite.addTest(unittest.makeSuite(MatpowerReaderTest))
#    suite.addTest(unittest.makeSuite(PSSEReaderTest))
#    suite.addTest(unittest.makeSuite(PSATReaderTest))

    return suite


if __name__ == '__main__':
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    unittest.TextTestRunner(verbosity=2).run(suite())

# EOF -------------------------------------------------------------------------
