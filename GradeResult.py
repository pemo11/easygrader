# file: GradeResult.py
from datetime import datetime

'''
Defines the result of a grading action for the grade report
'''
class GradeResult:

    def __init__(self, type):
        self.timestamp = datetime.now()
        self.type = type
        self.description = ""
        self.points = 0
        # compiles better name?
        self.success = False
        self.submission = None
        self.remarks = "No Paseran"
        self.message = ""

    def __repr__(self):
        return f"Type: {self.type} Description: {self.description} Student: {self.submission.studentId} Points: {self.points } Sucess: {self.success}"
