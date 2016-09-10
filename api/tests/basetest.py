from flask_testing import TestCase
import unittest
import pdb 
from server import app

class MyTest(TestCase):

    TESTING = True

    def create_app(self):

        # pass in test configuration
        return create_app(self)

    def setUp(self):
        print 'ZOMGOZOGMO'
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()

