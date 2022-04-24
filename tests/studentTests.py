# file: studentTests.py

import os
import sys
import unittest
import configparser

# Add the parent directory to the lib path
lib_path = os.path.abspath(os.path.join(__file__, '..'))
sys.path.append(lib_path)

from DBHelper import DBHelper

class TestRunner(unittest.TestCase):

    def setUp(self) -> None:
        config = configparser.ConfigParser()
        config.read("../Simpelgrader.ini")
        self.dbPath = config["path"]["dbPath"]

    '''
    Get student id from firstname lastname
    '''
    def testStudent1(self):
        student = "Peter Monadjemi"
        id = DBHelper.getStudentId(self.dbPath, student)
        self.assertTrue(id == 1001)


    '''
    Get student id from firstname_lastname
    '''
    def testStudent2(self):
        student = "Peter_Monadjemi"
        id = DBHelper.getStudentId(self.dbPath, student)
        self.assertTrue(id == 1001)

    '''
    Get student id from last name only
    '''
    def testStudent3(self):
        student = "Monadjemi"
        id = DBHelper.getStudentId(self.dbPath, student)
        self.assertTrue(id == 1001)

    '''
    Search for student id by lastname 
    '''
    def testStudent4(self):
        student = "Monadjemi"
        idList = DBHelper.searchStudentId(self.dbPath, student)
        self.assertTrue(len(idList) > 0)
