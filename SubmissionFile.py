# file: SubmissionFile.py
import re

'''
Represents the "meta data" of a submission file name
'''
class SubmissionFile:

    def __init__(self, submissionFile):
        # subnamePattern1 = "(?P<task>\w+)_Level(?P<level>\w)_(?P<student>[_\w]+)\.zip"
        # Der "Trick des Jahres" - non greedy dank *? anstelle von +, damit der Vorname nicht dem Aufgabenname zugeordnet wird
        # subnamePattern = "(?P<task>\w*?)_(?P<student>[_\w]+)\.zip"
        subnamePattern = "(?P<exercise>\w*?)_(?P<first>[\w]+)_(?P<last>[\w]+)\.zip"
        # nameElements = list(re.finditer(subnamePattern, submissionFile))
        # findall only returns a list - use finditer to get the named capture groups
        # eg. list(re.finditer(pa, fiName))[0].group("exercise")
        matchList = re.findall(subnamePattern, submissionFile)
        # all matches matched?
        if len(matchList) == 3:
            exercise = matchList[0]
            # does the exercise name ends with the level (eg. EA1A)?
            if len(exercise) == 4:
                level = exercise[3]
                exercise = exercise[0:3]
            else:
                level = "A"
            first = matchList[1]
            last = matchList[2]
            self.exercise = exercise
            self.student = f"{first}_{last}"
            self.level = level

    def __repr__(self):
        return f"Student: {self.student} Exercise: {self.exercise} Level: {self.level}"
