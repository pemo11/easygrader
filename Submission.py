# File: Submission.py
from datetime import datetime

'''
A single submission by a student
'''

class Submission:

    def __init__(self, id, student):
        self.id = id
        self.timestamp = datetime.now()
        self.student = student;
        self.exercise = ""
        self.level = ""
        self.semester = ""

    def __repr__(self):
        return f"Id={self.id} Student={self.student} Task={self.exercise}/{self.level} Time={self.timestamp}"
