# file: GradeAction.py
from datetime import datetime

'''
Defines a single grading action for the grade report
'''
class GradeAction:

    def __init__(self, type):
        self.timestamp = datetime.now()
        self.type = type
        self.description = "None"
        self.result = "None"
        self.success = False
        self.submission = "None"
        self.student = "None"

    def __repr__(self):
        return f"Type: {self.type} Description: {self.description} Student: {self.student} Sucess: {self.success}"
