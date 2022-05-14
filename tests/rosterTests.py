# file: rosterTests.py

import os
import sys
import tempfile
import unittest

# Add the parent directory to the lib path
lib_path = os.path.abspath(os.path.join(__file__, '..'))
sys.path.append(lib_path)

import RosterHelper

class TestRunner(unittest.TestCase):

    '''
    Read matriculation id from a java file
    '''
    def testCreateRoster(self):
        submissionPath = os.path.join(tempfile.gettempdir(), "ziptest")
        rosterPath = "testRoster.csv"
        result = RosterHelper.createStudentRoster(submissionPath, rosterPath)
        self.assertTrue(result)
