# file: gradingActionTests.py

import os
import sys
import unittest

# Add the parent directory to the lib path
lib_path = os.path.abspath(os.path.join(__file__, '..'))
sys.path.append(lib_path)

from XmlHelper import XmlHelper

class TestRunner(unittest.TestCase):

    '''
    Read action points from grading plan xml
    '''
    def testActionPoints(self):
        gradingPlanPath = os.path.join(os.path.dirname(__file__), "gradingplan1.xml")
        xmlHelper = XmlHelper(gradingPlanPath)
        result = xmlHelper.getActionPoints("EA1", "A01")
        self.assertTrue(result == 1)
