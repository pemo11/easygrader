# Test functions for XmlHelper.py and the grading plan xml
import os
import sys
import unittest

# Add the parent directory to the lib path
lib_path = os.path.abspath(os.path.join(__file__, '..'))
sys.path.append(lib_path)

from XmlHelper import XmlHelper

class TestRunner(unittest.TestCase):

    '''
    Read matriculation id from a java file
    '''
    def testTextCompare(self):
        gradingPlanPath = os.path.join(os.path.dirname(__file__), "gradingplan1.xml")
        xmlHelper = XmlHelper(gradingPlanPath)
        result = xmlHelper.getTextCompareTest("EA1")
        self.assertTrue(result != None)

    '''
    Read a test point from the grading xml file
    '''
    def testTestPoints(self):
        gradingPlanPath = os.path.join(os.path.dirname(__file__), "gradingplan1.xml")
        xmlHelper = XmlHelper(gradingPlanPath)
        result = xmlHelper.getTestPoints("EA1", "T01")
        self.assertTrue(result == 1)

    '''
    Read exercise points from the grading xml file
    '''
    def testExercisePoints(self):
        gradingPlanPath = os.path.join(os.path.dirname(__file__), "gradingplan1.xml")
        xmlHelper = XmlHelper(gradingPlanPath)
        result = xmlHelper.getExercisePoints("EA1")
        self.assertTrue(result == 6)
