# file: GradeAction.py
from datetime import datetime

'''
Defines the result of a grading action for the grade report
TODO: split GradeAction and GradeResult or rename to GradeResult?
'''
class GradeAction:

    def __init__(self, type):
        self.timestamp = datetime.now()
        self.type = type
        self.description = "None"
        self.points = 0
        # compiles better name?
        self.success = False
        self.submission = "None"
        self.student = "None"
        self.errorMessage = "None"

    def __repr__(self):
        return f"Type: {self.type} Description: {self.description} Student: {self.student} Points: {self.points }Sucess: {self.success}"
