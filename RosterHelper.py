# file: RosterHelper.py

import DBHelper
import Loghelper
import csv

''''
Stores the roster CSV file into the database
'''
def saveRosterInDb(dbPath, semester, module, csvPath) -> None:
    try:
        with open(csvPath, mode="r", encoding="utf8") as fh:
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
        infoMessage = f"saveRosterInDb: Roster from {csvPath} file was saved in db"
        Loghelper.logInfo(infoMessage)
    except Exception as ex:
        infoMessage = f"saveRosterInDb: {ex}"
        Loghelper.logError(infoMessage)

''''
Updates the roster with the submissions
'''
def updateStudentRoster():
    pass

