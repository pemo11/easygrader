# file: SubmissionName.py
import re

import Loghelper

'''
Represents the "meta data" of a submission file or directory name
'''
class SubmissionName:

    def __init__(self, submissionName):
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
        if len(list(re.finditer(subnamePattern1, submissionName))) > 0:
            matchList = list(re.finditer(subnamePattern1, submissionName))[0].groups()
            # all matches matched?
            if len(matchList) == 3:
                exercise = matchList[0]
                first = matchList[1]
                last = matchList[2]
                self.exercise = exercise
                self.student = f"{first}_{last}"
        # does the exercise_name pattern fits?
        elif len(list(re.finditer(subnamePattern2, submissionName))) > 0:
            matchList = list(re.finditer(subnamePattern2, submissionName))[0].groups()
            # all matches matched?
            if len(matchList) == 2:
                exercise = matchList[0]
            lastname = matchList[1]
            self.exercise = exercise
            self.student = f"{lastname}"
        else:
            # should not happen but...
            self.exercise = ""
            self.student = ""
            infoMessage = f"SubmissionName: {submissionName} does not match the name patterns"
            Loghelper.logError(infoMessage)

    def __repr__(self):
        return f"Student: {self.student} Exercise: {self.exercise}"
