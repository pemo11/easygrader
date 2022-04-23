# file: RosterHelper.py
import re

import DBHelper
import Loghelper
import csv

''''
Stores the roster CSV file into the database
'''
def saveRosterInDb(dbPath, semester, module, rosterPath) -> None:
    try:
        with open(rosterPath, mode="r", encoding="utf8") as fh:
            csvReader = csv.reader(fh, delimiter=",")
            # Immer wieder genial
            keys = next(fh).split(",")
            # Letztes \n abtrennen (auch irgendwie genial)
            keys[-1] = keys[-1].strip()
            for row in csvReader:
                studentName = row[0]
                studentId = row[1]
                studentMail = row[2]
                # store student in database
                DBHelper.storeStudent(dbPath, studentId, studentName, studentMail)
                exercises = ",".join(row[3:])
                # store roster entry in database
                DBHelper.storeRoster(dbPath, semester, module, studentId, exercises)
        infoMessage = f"saveRosterInDb: Roster from {rosterPath} file was saved in db"
        Loghelper.logInfo(infoMessage)
    except Exception as ex:
        infoMessage = f"saveRosterInDb: {ex}"
        Loghelper.logError(infoMessage)

'''
Validates the roster file for missing columns and unique keys
'''
def validateRoster(rosterPath) -> bool:
    try:
        with open(rosterPath, mode="r", encoding="utf8") as fh:
            csvReader = csv.reader(fh, delimiter=",")
            # Immer wieder genial
            csvKeys = next(fh).split(",")
            # Letztes \n abtrennen (auch irgendwie genial)
            csvKeys[-1] = csvKeys[-1].strip()
            # check for all keys
            keysNeeded = ["Name","StudentId","EMail","Exercises"]
            for key in keysNeeded:
                if not key in keysNeeded:
                    infoMessage = f"validateRoster->missing {key} in {rosterPath}"
                    Loghelper.logError(infoMessage)
                    return False

            # check for unique ids
            dictId = {}
            for row in csvReader:
                studentId = row[1]
                if dictId.get(studentId) != None:
                    infoMessage = f"validateRoster->{studentId} is not unique in {rosterPath}"
                    Loghelper.logError(infoMessage)
                    return False

            # check for valid email address
            # TODO: Better pattern
            mailPattern = "(.+)@(.+)"
            for row in csvReader:
                studentMail = row[2]
                if not re.match(mailPattern, studentMail):
                    infoMessage = f"validateRoster->{studentMail} is not valid in {rosterPath}"
                    Loghelper.logError(infoMessage)
                    return False

            return True
    except Exception as ex:
        infoMessage = f"validateRoster: {ex}"
        Loghelper.logError(infoMessage)

'''
Updates the roster with the submissions
'''
def updateStudentRoster(dbPath, submissionDic) -> None:
    exerciseCount = 0
    for exercise in submissionDic:
        for studentName in submissionDic[exercise]:
            for submission in submissionDic[exercise][studentName]:
                studentId = submission.studentId
                if studentId == None:
                    infoMessage = f"updateStudentRoster: no studentId for {studentName}"
                    Loghelper.logError(infoMessage)
                else:
                    exercise = submission.exercise
                    # update the exercise in the student roster
                    if DBHelper.updateRoster(dbPath, studentId, exercise):
                        exerciseCount += 1
    infoMessage = f"updateStudentRoster: roster update completed for {exerciseCount} exercises"
    Loghelper.logInfo(infoMessage)

