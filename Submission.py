# File: Submission.py
from datetime import datetime

'''
Defines a single submission by a student
'''
class Submission:

    def __init__(self, id, student):
        self.id = id
        self.timestamp = datetime.now()
        self.student = student
        self.fileName = ""
        self.semester = ""
        self.module = ""
        self.exercise = ""
        self.level = ""

    def __repr__(self):
        return f"Id={self.id} Student={self.student} Exercise={self.exercise}/{self.level} Time={self.timestamp}"
