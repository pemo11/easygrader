# file: DBHelper.py

import sqlite3
from sqlite3 import Error
import Loghelper
import os

from Submission import Submission

'''
Creates the database file and the tables without any data
'''
def initDb(dbPath):
    try:
        dbCon = sqlite3.connect(dbPath)
        infoMessage = f"Datenbank {dbPath} wurde angelegt (SQlite-Version: {sqlite3.version}) ***"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Anlegen der Datenbank: {ex}"
        Loghelper.logError(infoMessage)
    finally:
        dbCon.close()
        infoMessage = "Datenbankverbindung wurde geschlossen."
        Loghelper.logInfo(infoMessage)

    # Tabelle GradRun anlegen
    sqlKommando = """
    CREATE TABLE IF NOT EXISTS GradeRun (
     Id integer PRIMARY KEY AUTOINCREMENT,
     Timestamp datetime NOT NULL,
     Semester text NOT NULL,
     Module text NOT NULL,
     Operator text NOT NULL,
     SubmissionCount integer NOT NULL,
     OKCount integer NOT NULL,
     ErrorCount integer NOT NULL
    );
    """

    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.execute(sqlKommando)
        infoMessage = f"Tabelle GradeRun wurde angelegt"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Anlegen der Tabelle GradeRun {ex}"
        Loghelper.logError(infoMessage)
    finally:
        dbCon.close()
        infoMessage = "Datenbankverbindung wurde geschlossen."
        Loghelper.logInfo(infoMessage)

    # Tabelle Submission anlegen
    sqlKommando = """
    CREATE TABLE IF NOT EXISTS Submission (
     Id integer PRIMARY KEY AUTOINCREMENT,
     Timestamp datetime NOT NULL,
     Semester text NOT NULL,
     Module text NOT NULL,
     Exercise text NOT NULL,
     StudentId integer NOT NULL,
     Files text,
     Complete boolean NOT NULL
    );
    """
    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.execute(sqlKommando)
        infoMessage = f"Tabelle Submission wurde angelegt"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Anlegen der Tabelle Submission {ex}"
        Loghelper.logError(infoMessage)
    finally:
        dbCon.close()
        infoMessage = "Datenbankverbindung wurde geschlossen."
        Loghelper.logInfo(infoMessage)

    # Tabelle SubmissionResult anlegen
    sqlKommando = """
    CREATE TABLE IF NOT EXISTS SubmissionResult (
     Id integer PRIMARY KEY AUTOINCREMENT,
     GradeRun integer NOT NULL,
     StudentId integer NOT NULL,
     Exercise text NOT NULL,
     Level text NOT NULL,
     Semester text NOT NULL,
     Module text NOT NULL,
     Filename text,
     ResultPoints integer,
     ResultComment text,
     ResultRemarks text
    );
    """
    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.execute(sqlKommando)
        infoMessage = f"Tabelle SubmissionResult wurde angelegt"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Anlegen der Tabelle SubmissionResult {ex}"
        Loghelper.logError(infoMessage)
    finally:
        dbCon.close()
        infoMessage = "Datenbankverbindung wurde geschlossen."
        Loghelper.logInfo(infoMessage)

    # Tabelle Student anlegen
    sqlKommando = """
    CREATE TABLE IF NOT EXISTS Student (
     Id integer PRIMARY KEY,
     Firstname text,
     Lastname text NOT NULL,
     EMail text,
     Remarks text
    );
    """
    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.execute(sqlKommando)
        infoMessage = f"Tabelle Student wurde angelegt"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Anlegen der Tabelle Student {ex}"
        Loghelper.logError(infoMessage)
    finally:
        dbCon.close()
        infoMessage = "Datenbankverbindung wurde geschlossen."
        Loghelper.logInfo(infoMessage)

    # Tabelle Roster anlegen
    sqlKommando = """
    CREATE TABLE IF NOT EXISTS Roster (
     StudentId integer PRIMARY KEY,
     Semester text,
     Module text,
     Exercises text
    );
    """
    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.execute(sqlKommando)
        infoMessage = f"Tabelle Roster wurde angelegt"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Anlegen der Tabelle Roster {ex}"
        Loghelper.logError(infoMessage)
    finally:
        dbCon.close()
        infoMessage = "Datenbankverbindung wurde geschlossen."
        Loghelper.logInfo(infoMessage)

'''
Stores a grade run 
'''
def storeGradeRun(dbPath, timestamp, semester, module, operator, submissionCount, okCount, errorCount):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Insert Into GradeRun (Timestamp,Semester,Module, Operator,SubmissionCount,"
    sqlKommando += f"OKCount,ErrorCount) Values('{timestamp}','{semester}','{module}','{operator}',"
    sqlKommando += f"{submissionCount},{okCount},{errorCount})"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlKommando)
        dbCon.commit()
        infoMessage = f"Ein Datensatz wurde zur Tabelle GradeRun hinzugefügt"
        Loghelper.logInfo(infoMessage)
        # return the id of the new record
        return dbCur.lastrowid
    except Error as ex:
        infoMessage = f"Fehler beim Einfügen eines Datensatzes in die GradeRun-Tabelle {ex}"
        Loghelper.logError(infoMessage)

    dbCon.close()

'''
Stores a single submission of a student
'''
def storeSubmission(dbPath, timestamp, semester, module, exercise, studentId, files, complete):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Insert Into Submission (Timestamp,Semester,Module,Exercise,StudentId,Files,Complete) "
    sqlKommando += f"Values('{timestamp}','{semester}','{module}','{exercise}',"
    sqlKommando += f"'{studentId}','{files}','{complete}')"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlKommando)
        dbCon.commit()
        infoMessage = f"Ein Datensatz wurde zur Tabelle Submission hinzugefügt"
        Loghelper.logInfo(infoMessage)
        # return the id of the new record
        return dbCur.lastrowid
    except Error as ex:
        infoMessage = f"Fehler beim Einfügen eines Datensatzes in die Submission-Tabelle {ex}"
        Loghelper.logError(infoMessage)

    dbCon.close()

'''
Clears all the submission
'''
def clearAllSubmission(dbPath):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Delete From Submission"
    try:
        dbCon.execute(sqlKommando)
        dbCon.commit()
        infoMessage = f"Alle Datensätze in der Tabelle Submission wurden gelöscht"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Löschen aller Datensätze in die Submission-Tabelle {ex}"
        Loghelper.logError(infoMessage)

    dbCon.close()

'''
Gets all submisssions
'''
def getSubmissions(dbPath) -> dict:
    dict = {}
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return dict

    # group by als Alternative?
    sqlKommando = "Select * From Submission"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlKommando)
        rows = cur.fetchall()
        for row in rows:
            exercise = row[1]
            student = row[2]
            files = row[3]
            if dict.get(exercise) == None:
                dict[exercise] = {}
            if dict[exercise].get(student) == None:
                dict[exercise][student] = []
            submission = Submission()
            submission.student = row["student"]
            dict[exercise][student].append(submission)

    except Error as ex:
        infoMessage = f"Fehler beim Abfragen der Submission-Tabelle {ex}"
        Loghelper.logError(infoMessage)

    return dict

'''
Gets all submissions by a student name
'''
def getSubmissionByStudent(dbPath, student) -> [Submission]:
    submissions = []
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return submissions

    sqlKommando = "Select * From Submission Where Student = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlKommando, (student,))
        rows = cur.fetchall()
        for row in rows:
            submission = Submission()
            submission.student = row["student"]
            submissions.append(submission)
    except Error as ex:
        infoMessage = f"Fehler beim Abfragen der Submission-Tabelle {ex}"
        Loghelper.logError(infoMessage)
    return submissions

'''
Stores the grading for a single submission during a grade run
'''
def storeSubmissionResult(dbPath, gradeRunId, student, exercise, level, semester, module, filename, resultPoints, resultRemarks):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Insert Into SubmissionResult (GradeRun,Student,Exercise,Level,Semester,Module,Filename,ResultPoints,ResultRemarks) "
    sqlKommando += f"Values({gradeRunId}, '{student}','{exercise}','{level}','{semester}',"
    sqlKommando += f"'{module}','{filename}','{resultPoints}','{resultRemarks}')"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlKommando)
        dbCon.commit()
        infoMessage = f"Ein Datensatz wurde zur Tabelle SubmissionResult hinzugefügt"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Einfügen eines Datensatzes in die SubmissionResult-Tabelle {ex}"
        Loghelper.logError(infoMessage)

    dbCon.close()

'''
Gets all grade runs
'''
def getAllGradeRun(dbPath):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Select * From GradeRun"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlKommando)
        rows = cur.fetchall()
        return rows
    except Error as ex:
        infoMessage = f"Fehler beim Abfragen der GradeRun-Tabelle {ex}"
        Loghelper.logError(infoMessage)

'''
Gets a grade run by id
'''
def getGradeRun(dbPath, runId):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Select * From GradeRun Where Id = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlKommando, (runId,))
        row = cur.fetchone()
        if row == None:
            return 0
        else:
            return row[0]
    except Error as ex:
        infoMessage = f"Fehler beim Abfragen der GradeRun-Tabelle {ex}"
        Loghelper.logError(infoMessage)

'''
Get all submission results
'''
def getAllSubmissionResult(dbPath):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Select * From SubmissionResult"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlKommando)
        rows = cur.fetchall()
        return rows
    except Error as ex:
        infoMessage = f"Fehler beim Abfragen der SubmissionResult-Tabelle {ex}"
        Loghelper.logError(infoMessage)

'''
Get all the submission results for a single student
'''
def getSubmissionResultByStudent(dbPath, student):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Select * From SubmissionResult Where Student = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlKommando, (student,))
        rows = cur.fetchall()
        return rows
    except Error as ex:
        infoMessage = f"Fehler beim Abfragen der SubmissionResult-Tabelle {ex}"
        Loghelper.logError(infoMessage)
        return None

'''
get student name by id
'''
def getStudentById(dbPath, studentId):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Select StudentName,StudentMail From Student Where Id = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlKommando, (studentId,))
        row = cur.fetchone()
        return (row[0], row[1])
    except Error as ex:
        infoMessage = f"Fehler beim Abfragen der Student-Tabelle {ex}"
        Loghelper.logError(infoMessage)
        return None


'''
stores a student
'''
def storeStudent(dbPath, studentId, studentName, studentEMail) -> int:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return -1

    # check if student id already exists
    sqlKommando = f"Select Id From Student Where Id=?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlKommando, (studentId,))
        row = cur.fetchone()
        # any data?
        if row != None:
            # what data to return?
            infoMessage = f"Student with id={row[0]} already exists"
            Loghelper.logInfo(infoMessage)
            return row[0]
    except Error as ex:
        infoMessage = f"error querying student table {ex}"
        Loghelper.logError(infoMessage)
        return -1

    # insert new row
    try:
        remarks = ""
        if len(studentName.split("_")) > 0:
            firstName, lastName = studentName.split(" ")
        else:
            firstName = ""
            lastName = studentName
        sqlKommando = f"Insert Into Student (Id, FirstName, LastName, EMail, Remarks) "
        sqlKommando += f"Values ('{studentId}','{firstName}','{lastName}','{studentEMail}', '{remarks}')"
        dbCur = dbCon.cursor()
        dbCur.execute(sqlKommando)
        dbCon.commit()
        infoMessage = f"Ein Datensatz wurde zur Tabelle Student hinzugefügt (id={dbCur.lastrowid})"
        Loghelper.logInfo(infoMessage)
        # return the id of the new record
        return dbCur.lastrowid
    except Error as ex:
        infoMessage = f"Fehler beim Einfügen eines Datensatzes in die Student-Tabelle ({ex})"
        Loghelper.logError(infoMessage)
        return -1


'''
stores a student roster 
'''
def storeRoster(dbPath, semester, module, studentId, exercises) -> int:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)

    try:
        studentId = int(studentId)
        sqlKommando = f"Insert Into Roster Values ({studentId},'{semester}','{module}','{exercises}')"
        dbCur = dbCon.cursor()
        dbCur.execute(sqlKommando)
        dbCon.commit()
        infoMessage = f"Ein Datensatz wurde zur Tabelle Roster hinzugefügt (id={dbCur.lastrowid})"
        Loghelper.logInfo(infoMessage)
        # return the id of the new record
        return dbCur.lastrowid
    except Error as ex:
        infoMessage = f"Fehler beim Einfügen eines Datensatzes in die Roster-Tabelle ({ex})"
        Loghelper.logError(infoMessage)

    dbCon.close()
