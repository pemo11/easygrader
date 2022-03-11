# file: GradeAction.py
from datetime import datetime

# represents a grading action - not a result
class GradeAction:

    def __init__(self, type, action):
        self.type = type
        self.action = action
        self.timestamp = datetime.now()
        self.student = ""
        self.javaFile = ""

    def __repr__(self):
        return f"Type={self.type} Action={self.action} Student={self.student} with {self.javaFile}"
