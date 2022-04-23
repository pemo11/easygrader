# file: SubmissionValidation.py

from datetime import datetime

'''
Represents a single submission validation
'''
class SubmissionValidation:

    def __init__(self, exercise, type, message):
        self.exercise = exercise
        self.timestamp = datetime.now()
        self.type = type
        self.message = message
        self.studentId = 0
        self.submissionId = 0


    def __repr__(self):
        return f"Exercise: {self.exercise} Type: {self.type} Message: {self.message}"
