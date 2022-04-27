# File: Submission.py
from datetime import datetime

'''
Defines a single submission by a student id
'''
class Submission:

    def __init__(self, id, studentId):
        self.timestamp = datetime.now()
        self.id = id
        self.studentId = studentId
        self.semester = ""
        self.module = ""
        self.exercise = ""
        self.files = ""
        self.path = ""
        self.complete = False

    def __repr__(self):
        return f"Id={self.id} Student={self.studentId} Exercise={self.exercise} Time={self.timestamp}"
