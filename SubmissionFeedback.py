# file: SubmissionFeedback.py
# the feedback for a single submission

class SubmissionFeedback:

    def __init__(self, studentId):
        self.studentId = studentId
        self.exercise = ""
        self.testCount = 0
        self.totalPoints = 0
        self.feedbackText = ""


