# file: SubmissionValidationEntry.py

from datetime import datetime

'''
Represents a single submission error
'''
class SubmissionValidationEntry:

    def __init__(self, type, message):
        self.timestamp = datetime.now()
        self.type = type
        self.message = message


