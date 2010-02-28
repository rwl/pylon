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

""" Test case for the AC OPF routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest
from os.path import join, dirname

from pylon.readwrite import PickleReader
from pylon import ACOPF

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#------------------------------------------------------------------------------
#  "ACOPFTest" class:
#------------------------------------------------------------------------------

class ACOPFTest(unittest.TestCase):
    """ We use a MATPOWER data file and validate the results against those
        obtained from running the MATPOWER runopf.m script with the same data
        file and the FMINCON (fmincopf.m) algorithm.

        See reader_test_case.py for validation of MATPOWER data file parsing.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        case = self.case = PickleReader().read(DATA_FILE)
        self.routine = ACOPF(case)


    def test_mismatch(self):
        """ Test AC OPF.
        """
        solution = self.routine.solve()

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
