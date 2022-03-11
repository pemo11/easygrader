# file: GradeAction.py

# represents a grading action - not a result
class GradeAction:

    def __init__(self, action):
        self.action = action

    def __repr__(self):
        return f"Action={self.action}"
