# File: Submission.py
from datetime import datetime

'''
Defines a single submission by a student id
'''
class Submission:

    def __init__(self, id, studentId):
        self.timestamp = datetime.now().strftime("%d.%m.%y %H:%M")
        self.id = id
        self.studentId = studentId
        self.semester = ""
        self.module = ""
        self.exercise = ""
        self.level = ""
        self.files = ""

    def __repr__(self):
        return f"Id={self.id} Student={self.studentId} Exercise={self.exercise}/{self.level} Time={self.timestamp}"
