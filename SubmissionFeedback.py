# file: SubmissionFeedback.py
# the feedback for a single submission by a student
from datetime import datetime

class SubmissionFeedback:

    def __init__(self, studentId):
        self.timestamp = datetime.now()
        self.studentId = studentId
        self.exercise = ""
        self.actionCount = 0
        self.testCount = 0
        self.exercisePoints = 0
        self.totalPoints = 0
        self.actionSummary = ""
        self.testSummary = ""
        self.feedbackSummary = ""


