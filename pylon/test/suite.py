#------------------------------------------------------------------------------
# Copyright (C) 2007-2010 Richard Lincoln
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

from pylon.test.case_test import \
    CaseTest, BusTest, BranchTest, CaseMatrixTest, CaseMatrix24RTSTest, \
    CaseMatrixIEEE30Test

from pylon.test.generator_test import \
    GeneratorTest, OfferBidToPWLTest

from dcpf_test import \
    DCPFTest, DCPFCase24RTSTest, DCPFCaseIEEE30Test
from acpf_test import \
    ACPFTest, ACPFCase24RTSTest, ACPFCaseIEEE30Test
from opf_test import \
    DCOPFTest, DCOPFCase24RTSTest, DCOPFCaseIEEE30Test
from opf_test import \
    DCOPFSolverTest, DCOPFSolverCase24RTSTest, DCOPFSolverCaseIEEE30Test
from opf_test import \
    PIPSSolverTest, PIPSSolverCase24RTSTest, PIPSSolvercaseIEEE30Test
from opf_model_test import \
    OPFModelTest

from reader_test import MatpowerReaderTest, PSSEReaderTest#, PSATReaderTest
from se_test import StateEstimatorTest

#------------------------------------------------------------------------------
#  "suite" function:
#------------------------------------------------------------------------------

def suite():
    """ Returns the Pylon test suite.
    """
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(CaseTest))
    suite.addTest(unittest.makeSuite(CaseMatrixTest))
    suite.addTest(unittest.makeSuite(CaseMatrix24RTSTest))
    suite.addTest(unittest.makeSuite(CaseMatrixIEEE30Test))
    suite.addTest(unittest.makeSuite(BusTest))
    suite.addTest(unittest.makeSuite(BranchTest))

    suite.addTest(unittest.makeSuite(GeneratorTest))
    suite.addTest(unittest.makeSuite(OfferBidToPWLTest))

    # Solver test cases.
    suite.addTest(unittest.makeSuite(DCPFTest))
    suite.addTest(unittest.makeSuite(DCPFCase24RTSTest))
    suite.addTest(unittest.makeSuite(DCPFCaseIEEE30Test))
    suite.addTest(unittest.makeSuite(ACPFTest))
    suite.addTest(unittest.makeSuite(ACPFCase24RTSTest))
    suite.addTest(unittest.makeSuite(ACPFCaseIEEE30Test))
    suite.addTest(unittest.makeSuite(DCOPFTest))
    suite.addTest(unittest.makeSuite(DCOPFCase24RTSTest))
    suite.addTest(unittest.makeSuite(DCOPFCaseIEEE30Test))
    suite.addTest(unittest.makeSuite(DCOPFSolverTest))
    suite.addTest(unittest.makeSuite(DCOPFSolverCase24RTSTest))
    suite.addTest(unittest.makeSuite(DCOPFSolverCaseIEEE30Test))
    suite.addTest(unittest.makeSuite(PIPSSolverTest))
    suite.addTest(unittest.makeSuite(PIPSSolverCase24RTSTest))
    suite.addTest(unittest.makeSuite(PIPSSolvercaseIEEE30Test))
    suite.addTest(unittest.makeSuite(OPFModelTest))

    # Read/write test cases.
    suite.addTest(unittest.makeSuite(MatpowerReaderTest))
    suite.addTest(unittest.makeSuite(PSSEReaderTest))
#    suite.addTest(unittest.makeSuite(PSATReaderTest))

    # State estimator test.
    suite.addTest(unittest.makeSuite(StateEstimatorTest))

    return suite


if __name__ == '__main__':
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    unittest.TextTestRunner(verbosity=2).run(suite())

# EOF -------------------------------------------------------------------------
