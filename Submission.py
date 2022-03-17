# File: Submission.py
from datetime import datetime

'''
Defines a single submission by a student
'''
class Submission:

    def __init__(self, id, student):
        self.timestamp = datetime.now()
        self.id = id
        self.student = student
        self.semester = ""
        self.module = ""
        self.exercise = ""
        self.level = ""
        self.filePath = ""

    def __repr__(self):
        return f"Id={self.id} Student={self.student} Exercise={self.exercise}/{self.level} Time={self.timestamp}"
