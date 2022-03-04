# file: GradeReport.py

from datetime import datetime

'''
Defines the report with all the actions for a grading run
'''

class GradeReport:

    def __init__(self):
        self.creationDate = datetime.now()

    def addAction(self, action):
        pass
