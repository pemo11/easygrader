# file: RosterHelper.py
import re
import os
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

'''
splits a student name into first last name
there is only one last name part every name before that name is part of the first name part
if the last name is a double name it has to be "name1-name2"
'''
def getFirstLastName(studentName):
    nameElements = studentName.split(" ")
    if len(nameElements) == 1:
        return ("", studentName)
    elif len(nameElements) == 2:
        return tuple(nameElements)
    elif len(nameElements) > 2:
        firstName = " ".join(nameElements[0:-1])
        lastName = nameElements[-1]
        return (firstName, lastName)

'''
extract e-mail-address from a source file
'''
def getStudEMail(filePath, emailPattern = "stud\.hs-emden-leer\.de") -> str:
    email = ""
    with open(filePath, mode="r", encoding="cp1252") as fh:
        for line in  fh:
            if len(re.findall(rf"author.*(\w+@{emailPattern})", line)) > 0:
                email = re.findall(rf"author.*?([\w\.]+@{emailPattern})", line)[0]
                return email
    return email

'''
creates a student roster csv based on the submission directory
'''
def createStudentRoster(submissionPath, rosterPath, startId=1000) -> bool:
    studDic = {}
    # go through all subdirectories of the submission directory
    for studName in os.listdir(submissionPath):
        studDirPath = os.path.join(submissionPath, studName)
        # go through all the files in the submission directory
        for studFile in os.listdir(studDirPath):
            # file already in the dict?
            if studDic.get(studName) == None:
                studFilePath = os.path.join(studDirPath, studFile)
                # try to extract the email address from that file
                eMail = getStudEMail(studFilePath)
                if eMail != "":
                    studDic[studName] = (studName, str(startId), eMail)
        startId += 1
        if studDic.get(studName) == None:
            studDic[studName] = (studName, str(startId), "stud@nomail.org")
    # write the csv file
    # head line of the csv = "Name","StudentId","EMail","Exercises"
    try:
        with open(rosterPath, mode="w", encoding="cp1252") as fh:
            fh.write("Name,StudentId,EMail,Exercises\n")
            for studentName in studDic:
                fh.write(f"{','.join(studDic[studentName])},\n")
        infoMessage = "createStudentRoster: {rosterPath} written with {len(studDic)} entries"
        Loghelper.logInfo(infoMessage)
        return True
    except Exception as ex:
        infoMessage = "createStudentRoster: error writing {rosterPath} ({ex})"
        Loghelper.logWarning(infoMessage)
        return False
