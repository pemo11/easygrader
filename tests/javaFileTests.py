# Test functions for JavaFileHelper.py
import os
import sys
import unittest

# Add the parent directory to the lib path
lib_path = os.path.abspath(os.path.join(__file__, '..'))
sys.path.append(lib_path)

import JavaFileHelper

class TestRunner(unittest.TestCase):

    '''
    Read matriculation id from a java file
    '''
    def testMatrikelId(self):
        javaPath = os.path.join(os.path.dirname(__file__), "test.java")
        id = JavaFileHelper.getMatricleId(javaPath)
        self.assertTrue(id == "7004123")


