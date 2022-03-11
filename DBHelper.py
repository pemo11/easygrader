# file: DBHelper.py

import sqlite3
from sqlite3 import Error
import Loghelper
import os

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
        infoMessage = "*** Datenbankverbindung wurde geschlossen ***"
        Loghelper.logInfo(infoMessage)

    # Tabelle GradRun anlegen
    sqlKommando = """
    CREATE TABLE IF NOT EXISTS GradeRun (
     Id integer PRIMARY KEY,
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
        infoMessage = "*** Tabelle GradeRun wurde angelegt ***"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Anlegen der Tabelle GradeRun {ex}"
        Loghelper.logError(infoMessage)
    finally:
        dbCon.close()
        infoMessage = "*** Datenbankverbindung wurde geschlossen ***"
        Loghelper.logInfo(infoMessage)

    # Tabelle SubmissionResult anlegen
    sqlKommando = """
    CREATE TABLE IF NOT EXISTS SubmissionResult (
     Id integer PRIMARY KEY,
     GradeRun integer NOT NULL,
     Student text NOT NULL,
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
        infoMessage = "*** Tabelle SubmissionResult wurde angelegt ***"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Anlegen der Tabelle SubmissionResult {ex}"
        Loghelper.logError(infoMessage)
    finally:
        dbCon.close()
        infoMessage = "*** Datenbankverbindung wurde geschlossen ***"
        Loghelper.logInfo(infoMessage)

'''
Stores a grade run 
'''
def storeGradeRun(dbPath, Timestamp, Semester, Module, Operator, SubmissionCount, OKCount, ErrorCount):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Insert Into GradeRun (Timestamp,Semester,Module, Operator,SubmissionCount,"
    sqlKommando += f"OKCount,ErrorCount) Values('{Timestamp}','{Semester}','{Module}','{Operator}',"
    sqlKommando += f"{SubmissionCount},{OKCount},{ErrorCount})"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlKommando)
        dbCon.commit()
        infoMessage = "*** Datensatz wurde zur Tabelle GradeRun hinzugefügt ***"
        Loghelper.logInfo(infoMessage)
        # return the id of the new record
        return dbCur.lastrowid
    except Error as ex:
        infoMessage = f"Fehler beim Einfügen eines Datensatzes in die GradeRun-Tabelle {ex}"
        Loghelper.logError(infoMessage)

    dbCon.close()

'''
Stores the grading for a single submission during a grade run
'''
def storeSubmissionResult(dbPath, GradeRunId, Student, Exercise, Level, Semester, Module, Filename, ResultPoints, ResultRemarks):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Insert Into SubmissionResult (GradeRun,Student,Exercise,Level,Semester,Module,Filename,ResultPoints,ResultRemarks) "
    sqlKommando += f"Values({GradeRunId}, '{Student}','{Exercise}','{Level}','{Semester}',"
    sqlKommando += f"'{Module}','{Filename}','{ResultPoints}','{ResultRemarks}')"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlKommando)
        dbCon.commit()
        infoMessage = "*** Datensatz wurde zur Tabelle SubmissionResult hinzugefügt ***"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Einfügen eines Datensatzes in die SubmissionResult-Tabelle {ex}"
        Loghelper.logError(infoMessage)

    dbCon.close()

'''
Gets all grade runs
'''
def getGradeRuns(dbPath):
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
def getSubmissionResults(dbPath):
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
def getStudentSubmissionResults(dbPath, Student):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Select * From SubmissionResult Where Student = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlKommando, (Student,))
        rows = cur.fetchall()
        return rows
    except Error as ex:
        infoMessage = f"Fehler beim Abfragen der SubmissionResult-Tabelle {ex}"
        Loghelper.logError(infoMessage)
        return None
