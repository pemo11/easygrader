# file: SubmissionFile.py
import re

import Loghelper

'''
Represents the "meta data" of a submission file name
'''
class SubmissionFile:

    def __init__(self, submissionFile):
        # subnamePattern1 = "(?P<task>\w+)_Level(?P<level>\w)_(?P<student>[_\w]+)\.zip"
        # Der "Trick des Jahres" - non greedy dank *? anstelle von +, damit der Vorname nicht dem Aufgabenname zugeordnet wird
        # subnamePattern = "(?P<task>\w*?)_(?P<student>[_\w]+)\.zip"
        # subnamePattern = "(?P<exercise>\w*?)_(?P<first>[\w]+)_(?P<last>[\w]+)\.zip"
        subnamePattern1 = "(?P<exercise>\w*?)_(?P<first>[\w]+)_(?P<last>[\w]+)"
        subnamePattern2 = "(?P<exercise>\w*?)_(?P<name>[\w]+)"
        # nameElements = list(re.finditer(subnamePattern, submissionFile))
        # findall only returns a list - use finditer to get the named capture groups
        # eg. list(re.finditer(pa, fiName))[0].group("exercise")

        # does the exercise_firstname_lastname-Pattern?
        if len(list(re.finditer(subnamePattern1, submissionFile))) > 0:
            matchList = list(re.finditer(subnamePattern1, submissionFile))[0].groups()
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
        # does the exercise_name pattern fits?
        elif len(list(re.finditer(subnamePattern2, submissionFile))) > 0:
            matchList = list(re.finditer(subnamePattern2, submissionFile))[0].groups()
            # all matches matched?
            if len(matchList) == 2:
                exercise = matchList[0]
            # does the exercise name ends with the level (eg. EA1A)?
            if len(exercise) == 4:
                level = exercise[3]
                exercise = exercise[0:3]
            else:
                level = "A"
            lastname = matchList[1]
            self.exercise = exercise
            self.student = f"{lastname}"
            self.level = level
        else:
            # should not happen but...
            self.exercise = ""
            self.student = ""
            self.level = ""
            infoMessage = f"SubmissionFile: {submissionFile} does not match the name patterns"
            Loghelper.logError(infoMessage)

    def __repr__(self):
        return f"Student: {self.student} Exercise: {self.exercise} Level: {self.level}"
