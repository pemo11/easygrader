# file: Roster.py

'''
Represents a single roster entry
'''
class Roster:

    def __init__(self, **kwargs):
        self.studentId = kwargs["StudentId"]
        self.semester = kwargs["Semester"]
        self.module = kwargs["Module"]
        self.exercises = kwargs["Exercises"]
        self.completed = kwargs["Completed"]

    def __repr__(self):
        return f"StudentId={self.studentId} Exercises={self.exercises} Completed={self.completed}"
