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

""" Data file parsing tests.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path

from time import time

from unittest import TestCase, main

from pylon.readwrite import \
    MATPOWERReader, PSSEReader, PSATReader, PickleReader, RDFReader, RDFWriter

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

MATPOWER_DATA_FILE = os.path.join(DATA_DIR, "case6ww.m")
PWL_MP_DATA_FILE   = os.path.join(DATA_DIR, "case30pwl.m")
UKGDS_DATA_FILE    = os.path.join(DATA_DIR, "ehv3.raw")
PSSE_DATA_FILE     = os.path.join(DATA_DIR, "sample30.raw")
BENCH_DATA_FILE    = os.path.join(DATA_DIR, "bench30.raw")
BENCH2_DATA_FILE   = os.path.join(DATA_DIR, "bench2_30.raw")
PSAT_DATA_FILE     = os.path.join(DATA_DIR, "d_006_mdl.m")
BENCH_PICKLE_FILE  = os.path.join(DATA_DIR, "bench30.pkl")
BENCH_RDFXML_FILE  = os.path.join(DATA_DIR, "bench30.rdf")

#------------------------------------------------------------------------------
#  "ReaderTest" class:
#------------------------------------------------------------------------------

class ReaderTest(TestCase):
    """ Defines a base class for many reader test cases.
    """

    def _validate_base(self, base_mva):
        """ Validate the Network objects properties.
        """

        c = self.case

        self.assertEqual(c.base_mva, base_mva)


    def _validate_object_numbers(self, n_buses, n_branches, n_gen):
        """ Validates the expected number of objects.
        """
        c = self.case

        self.assertEqual(len(c.buses), n_buses,
            "%d buses expected, %d found" % (n_buses, len(c.buses)))

        self.assertEqual(len(c.branches), n_branches,
            "%d branches expected, %d found" % (n_branches, len(c.branches)))

        self.assertEqual(len(c.generators), n_gen,
            "%d generators expected, %d found" % (n_gen,len(c.generators)))


    def _validate_slack_bus(self, slack_idx):
        """ Validates the location and number of slack buses.
        """
        c = self.case
        slack_idxs = [c.buses.index(v) for v in c.buses if v.type == "ref"]

        self.assertEqual(slack_idxs, [slack_idx])


    def _validate_generator_connections(self, gbus_idxs):
        """ Validates that generators are connected to the expected buses.
        """
        for i, g in enumerate(self.case.generators):
            busidx = self.case.buses.index(g.bus)
            self.assertEqual(busidx, gbus_idxs[i])


    def _validate_branch_connections(self, from_idxs, to_idxs):
        """ Validates that Branch objects are connected to the expected
            from and to buses.
        """
        c = self.case

        for e in c.branches:
            from_idx = c.buses.index(e.from_bus)
            from_expected = from_idxs[c.branches.index(e)]
            self.assertEqual(from_idx, from_expected,
                "From bus %d expected, %d found" %
                (from_expected, from_idx))

            to_idx = c.buses.index(e.to_bus)
            to_expected = to_idxs[c.branches.index(e)]
            self.assertEqual(to_idx, to_expected,
                "To bus %d expected, %d found" %
                (to_expected, to_idx))

#------------------------------------------------------------------------------
#  "MatpowerReaderTest" class:
#------------------------------------------------------------------------------

class MatpowerReaderTest(ReaderTest):
    """ Defines a test case for the MATPOWER reader.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.reader = MATPOWERReader()


    def test_case6ww(self):
        """ Test parsing case6ww.m file.
        """
        self.case = c = self.reader.read(MATPOWER_DATA_FILE)

        self._validate_base(base_mva=100.0)

        # Network structure validation.
        self._validate_object_numbers(n_buses=6, n_branches=11, n_gen=3)

        self._validate_slack_bus(slack_idx=0)

        self._validate_generator_connections(gbus_idxs=[0, 1, 2])

        self._validate_branch_connections(
            from_idxs=[0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 4],
            to_idxs=[1, 3, 4, 2, 3, 4, 5, 4, 5, 4, 5])

        # Generator costs.
        for g in c.generators:
            self.assertEqual(g.pcost_model, "poly")
            self.assertEqual(len(g.p_cost), 3)

        self.assertEqual(c.generators[0].p_cost[0], 0.00533)
        self.assertEqual(c.generators[1].p_cost[1], 10.333)
        self.assertEqual(c.generators[2].p_cost[2], 240)



    def test_case30pwl(self):
        """ Test parsing case30pwl.m.
        """
        case = self.case = self.reader.read(PWL_MP_DATA_FILE)

        self._validate_base(base_mva=100.0)

        self._validate_object_numbers(n_buses=30, n_branches=41, n_gen=6)

        self._validate_slack_bus(slack_idx=0)

        self._validate_generator_connections(gbus_idxs=[0, 1, 21, 26, 22, 12])

        self._validate_branch_connections(
            from_idxs=[0, 0, 1, 2, 1, 1, 3, 4, 5, 5, 5, 5, 8, 8, 3, 11, 11,
                       11, 11, 13, 15, 14, 17, 18, 9, 9, 9, 9, 20, 14, 21,
                       22, 23, 24, 24, 27, 26, 26, 28, 7, 5],
            to_idxs=[1, 2, 3, 3, 4, 5, 5, 6, 6, 7, 8, 9, 10, 9, 11, 12, 13,
                     14, 15, 14, 16, 17, 18, 19, 19, 16, 20, 21, 21, 22,
                     23, 23, 24, 25, 26, 26, 28, 29, 29, 27, 27])

        # Generator costs.
        generators = case.generators

        for g in generators:
            self.assertEqual(g.pcost_model, "pwl")
            self.assertEqual(len(g.p_cost), 4)
            self.assertEqual(g.p_cost[0], (0.0, 0.0))

        self.assertEqual(generators[0].p_cost[1], (12.0, 144.0))
        self.assertEqual(generators[4].p_cost[2], (36.0, 1296.0))
        self.assertEqual(generators[5].p_cost[3], (60.0, 2832.0))

#------------------------------------------------------------------------------
#  "PSSEReaderTest" class:
#------------------------------------------------------------------------------

class PSSEReaderTest(TestCase):
    """ Defines a test case for the PSS/E data file reader.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.reader = PSSEReader()


    def test_sample(self):
        """ Test parsing a sample PSS/E version 30 file.
        """
        case = self.reader.read(PSSE_DATA_FILE)

        self.assertEqual(len(case.buses), 42)
        pl = 5
        self.assertAlmostEqual(case.buses[0].v_base, 21.6, pl)
        self.assertAlmostEqual(case.buses[41].v_base, 0.69, pl)
        self.assertAlmostEqual(case.buses[0].v_magnitude_guess, 1.01, pl)
        self.assertAlmostEqual(case.buses[40].v_magnitude_guess, 1.04738, pl)
        self.assertAlmostEqual(case.buses[0].v_angle_guess, -10.4286, pl)
        self.assertAlmostEqual(case.buses[1].v_angle_guess, -10.7806, pl)

        # Loads.
        load_buses = [b for b in case.buses if
                      b.p_demand > 0.0 or b.q_demand > 0.0]
        self.assertEqual(len(load_buses), 15)
        self.assertAlmostEqual(case.buses[3].p_demand, 1200.0, pl)
        self.assertAlmostEqual(case.buses[3].q_demand, 360.0, pl)
        self.assertAlmostEqual(case.buses[34].p_demand, 12.0, pl)
        self.assertAlmostEqual(case.buses[34].q_demand, 5.0, pl)

        # Generators.
        self.assertEqual(len(case.generators), 15)
        self.assertAlmostEqual(case.generators[0].p, 750.0, pl)
        self.assertAlmostEqual(case.generators[0].q, 125.648, pl)
        self.assertAlmostEqual(case.generators[0].q_max, 400.0, pl)
        self.assertAlmostEqual(case.generators[0].q_min, -100.0, pl)
        self.assertAlmostEqual(case.generators[0].v_magnitude, 1.01, pl)
        self.assertAlmostEqual(case.generators[0].base_mva, 900.0, pl)
        self.assertTrue(case.generators[0].online)
        self.assertAlmostEqual(case.generators[0].p_max, 800.0, pl)
        self.assertAlmostEqual(case.generators[0].p_min, 50.0, pl)

        self.assertAlmostEqual(case.generators[14].p, 3.24, pl)
        self.assertAlmostEqual(case.generators[14].q, -1.475, pl)

        # Branches.
        self.assertEqual(case.buses.index(case.branches[0].from_bus), 2)
        self.assertEqual(case.buses.index(case.branches[0].to_bus), 3)
        self.assertEqual(case.branches[0].r, 0.00260, pl)
        self.assertEqual(case.branches[0].x, 0.04600, pl)
        self.assertEqual(case.branches[0].b, 3.50000, pl)
        self.assertEqual(case.branches[0].rate_a, 1200.00, pl)
        self.assertEqual(case.branches[0].rate_b, 1100.00, pl)
        self.assertEqual(case.branches[0].rate_c, 1000.00, pl)
        self.assertTrue(case.branches[0].online)

        self.assertEqual(case.buses.index(case.branches[29].from_bus), 32)
        self.assertEqual(case.buses.index(case.branches[29].to_bus), 33)

        # Transformers.
        self.assertEqual(case.buses.index(case.branches[30].from_bus), 0)
        self.assertEqual(case.buses.index(case.branches[30].to_bus), 2)
        self.assertEqual(case.branches[30].b, -0.10288, pl)
        self.assertEqual(case.branches[30].r, 0.00009, pl)
        self.assertEqual(case.branches[30].x, 0.00758, pl)
        self.assertEqual(case.branches[30].ratio, 1.0, pl)
        self.assertEqual(case.branches[30].phase_shift, 0.0, pl)
        self.assertEqual(case.branches[30].rate_a, 1200.00, pl)
        self.assertEqual(case.branches[30].rate_b, 1100.00, pl)
        self.assertEqual(case.branches[30].rate_c, 1000.00, pl)

        self.assertEqual(len(case.branches), 30 + 18 - 4) # 4 3-winding trx.


    def test_benchmark(self):
        """ Test parsing the benchmark case.
        """
        case = self.reader.read(BENCH_DATA_FILE)

        self.assertEqual(len(case.buses), 1648)
        self.assertEqual(len(case.branches), 2602)
        self.assertEqual(len(case.generators), 313)

#        from pylon.readwrite.pickle_readwrite import PickleWriter
#        PickleWriter(case).write("./data/bench30.pkl")


    def test_benchmark_two(self):
        """ Test parsing the second benchmark case.
        """
        case = self.reader.read(BENCH2_DATA_FILE)

        self.assertEqual(len(case.buses), 7917)
        self.assertEqual(len(case.branches), 13014)
        self.assertEqual(len(case.generators), 1325)


#    def test_ukgds(self):
#        """ Test parsing of PSS/E data file exported from the UKGDS.
#        """
#        # Parse the file.
#        self.case = self.reader.read(UKGDS_DATA_FILE)
#
#        # Network structure validation
#        self._validate_base(100.0)
#
#        self._validate_object_numbers(n_buses=102,
#                                      # 75 lines + 67 transformers = 142
#                                      n_branches=142,
#                                      n_gen=3)
#
#        self._validate_slack_bus(slack_idx=0)
#
#        self._validate_generator_connections(gbus_idxs=[0, 1])
#
#        self._validate_branch_connections(from_idxs=[0, 0, 1],
#                                          to_idxs=[1, 2, 2])

#------------------------------------------------------------------------------
#  "PSATReaderTest" class:
#------------------------------------------------------------------------------

#class PSATReaderTest(ReaderTest):
#    """ Defines a test case for the PSAT data file reader.
#    """
#
#    def test_psat(self):
#        """ Test parsing of a PSAT data file.
#        """
#        reader = PSATReader()
#        self.case = reader(PSAT_DATA_FILE)

#------------------------------------------------------------------------------
#  "PickleReaderTest" class:
#------------------------------------------------------------------------------

#class PickleReaderTest(TestCase):
#    """ Defines a test case for the pickle reader.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        self.reader = PickleReader()
#
#
#    def test_benchmark_case(self):
#        """ Test unpickling the benchmark case.
#        """
#        t0 = time()
#        case = self.reader.read(BENCH_PICKLE_FILE)
#        print "read elapse:", time() - t0
#
#        self.assertEqual(len(case.buses), 1648)
#        self.assertEqual(len(case.branches), 2602)
#        self.assertEqual(len(case.generators), 313)
#
##        from pylon.readwrite.pickle_readwrite import PickleWriter
##        t1 = time()
##        PickleWriter(case).write("/tmp/bench30.pkl")
##        print "write elapse:", time() - t1
#
##        from pylon.readwrite.rdf_readwrite import RDFWriter
##        RDFWriter(case).write("./data/bench.rdf")

#------------------------------------------------------------------------------
#  "RDFReadWriteTest" class:
#------------------------------------------------------------------------------

#class RDFReadWriteTest(TestCase):
#    """ Defines a test case for RDF reading/writing.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        self.reader = RDFReader()
#
#
#    def test_read_benchmark(self):
#        """ Test reading the RDF benchmark case.
#        """
#        t0 = time()
#        case = self.reader.read(BENCH_RDFXML_FILE)
#        print "Read RDF time:", time() - t0
#
##        self.assertEqual(len(case.buses), 1648)
##        self.assertEqual(len(case.branches), 2602)
##        self.assertEqual(len(case.generators), 313)


#    def test_write_benchmark(self):
#        """ Test write case as RDF.
#        """
#        case = PickleReader().read(BENCH_PICKLE_FILE)
#
#        RDFWriter(case).write("/tmp/bench30.rdf")

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")
    main()

# EOF -------------------------------------------------------------------------
