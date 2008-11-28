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

    unittest.TextTestRunner(verbosity=2).run(suite())
