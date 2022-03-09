# file: DBHelper.py

import sqlite3
from sqlite3 import Error
from pathlib import Path
import Loghelper
import os

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

def storeGradeRun(dbPath, Timestamp, Semester, Operator, SubmissionCount, OKCount, ErrorCount):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"Fehler beim Herstellen der Datenbankverbindung {ex}"
        Loghelper.logError(infoMessage)
        return

    sqlKommando = "Insert Into GradeRun (Timestamp,Semester,Operator,SubmissionCount,"
    sqlKommando += f"OKCount,ErrorCount) Values('{Timestamp}','{Semester}','{Operator}',"
    sqlKommando += f"{SubmissionCount},{OKCount},{ErrorCount})"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlKommando)
        dbCon.commit()
        infoMessage = "*** Datensatz wurde zur Tabelle GradeRun hinzugefügt ***"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"Fehler beim Einfügen eines Datensatzes in die GradeRun-Tabelle {ex}"
        Loghelper.logError(infoMessage)

    dbCon.close()

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

