# file: FeedbackItem.py
'''
Represents a single Feedback item
'''
class FeedbackItem:

    def __init__(self, id, submission):
        self.id = id
        self.submission = submission
        self.report = ""
        self.severity = "normal"

    def __repr__(self):
        return f"Id: {self.id} for Submission {self.submission.id}: {self.Report}/{self.severity}"
