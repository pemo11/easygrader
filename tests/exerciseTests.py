# file: exerciseTests.py

import os
import sys
import tempfile
import unittest

# Add the parent directory to the lib path
lib_path = os.path.abspath(os.path.join(__file__, '..'))
sys.path.append(lib_path)

from XmlHelper import XmlHelper

class TestRunner(unittest.TestCase):

    '''
    Read matriculation id from a java file
    '''
    def testExerciseActive(self):
        gradingPlanPath = os.path.join(os.path.dirname(__file__), "gradingplan1.xml")
        xmlHelper = XmlHelper(gradingPlanPath)
        exercise = "EA1"
        result = xmlHelper.exerciseActive(exercise)
        self.assertTrue(result)
