# file: rosterTests.py

import os
import sys
import tempfile
import unittest

# Add the parent directory to the lib path
lib_path = os.path.abspath(os.path.join(__file__, '..'))
sys.path.append(lib_path)

from RosterHelper import RosterHelper

class TestRunner(unittest.TestCase):

    def __init__(self):
        self.configPath = "simpelgrader.ini"

    '''
    Read matriculation id from a java file
    '''
    def testCreateRoster(self):
        submissionPath = os.path.join(tempfile.gettempdir(), "ziptest")
        rosterPath = "testRoster.csv"
        rosterHelper = RosterHelper(self.configPath)
        result = RosterHelper.createStudentRoster(submissionPath, rosterPath)
        self.assertTrue(result)
