# file: SubmissionFile.py
import re

'''
Represents the "meta data" of a submission file name
'''
class SubmissionFile:

    def __init__(self, submissionFile):
        subnamePattern1 = "(?P<task>\w+)_Level(?P<level>\w)_(?P<student>[_\w]+)\.zip"
        # Der "Trick des Jahres" - non greedy dank *? anstelle von +, damit der Vorname nicht dem Aufgabenname zugeordnet wird
        subnamePattern2 = "(?P<task>\w*?)_(?P<student>[_\w]+)\.zip"
        nameElements = list(re.finditer(subnamePattern1, submissionFile))
        if (len(nameElements) == 0):
            nameElements = list(re.finditer(subnamePattern2, submissionFile))
        self.excercise = nameElements[0].group("task")
        self.student = nameElements[0].group("student")
        self.level = nameElements[0].group("level") if len(nameElements) == 3 else "A"

    def __repr__(self):
        return f"Student: {self.student} Exercise: {self.exercise} Level: {self.level}"
