# Test functions for Submission.py
import os
import sys
import unittest

# Add the parent directory to the lib path
lib_path = os.path.abspath(os.path.join(__file__, '..'))
sys.path.append(lib_path)

import SubmissionHelper

class TestRunner(unittest.TestCase):

    '''
    Just a dummy test
    '''
    def testSubmission1(self):
        result = True
        self.assertTrue(result)


