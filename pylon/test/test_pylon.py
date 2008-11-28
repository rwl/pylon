import unittest

def suite():

    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(testBlogger))

    return suite



if __name__ == '__main__':

    #unittest.main()

    suiteFew = unittest.TestSuite()

    suiteFew.addTest(testBlogger("testPostNewEntry"))

    suiteFew.addTest(testBlogger("testDeleteAllEntries"))

    #unittest.TextTestRunner(verbosity=2).run(suiteFew)

    unittest.TextTestRunner(verbosity=2).run(suite())
