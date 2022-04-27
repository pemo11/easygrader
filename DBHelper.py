# file: DBHelper.py

import sqlite3
from sqlite3 import Error

import DBHelper
import Loghelper
import os

from Roster import Roster
from Submission import Submission
from Student import Student

'''
Creates the database file and the tables without any data
'''
def initDb(dbPath):
    dbCon = None

    try:
        dbCon = sqlite3.connect(dbPath)
        infoMessage = f"initDb: created database {dbPath} (SQlite-Version: {sqlite3.version}) ***"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"initDb: error connecting to database {ex}"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()
            infoMessage = "initDb: closed connection to database"
            Loghelper.logInfo(infoMessage)

    # Tabelle GradRun anlegen
    sqlCommand = """
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
        dbCon.execute(sqlCommand)
        infoMessage = f"Created table GradeRun"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"initDb: error connecting to database {ex}"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()
            infoMessage = "initDb: closed connection to database"
            Loghelper.logInfo(infoMessage)

    # Tabelle Submission anlegen
    sqlCommand = """
    CREATE TABLE IF NOT EXISTS Submission (
     Id integer PRIMARY KEY AUTOINCREMENT,
     Timestamp datetime NOT NULL,
     Semester text NOT NULL,
     Module text NOT NULL,
     Exercise text NOT NULL,
     StudentId integer NOT NULL,
     Files text,
     Path text,
     Complete boolean NOT NULL,
     Remarks text
    );
    """
    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.execute(sqlCommand)
        infoMessage = f"initDb: created table Submission"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"initDb: error creating Table Submission ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()
            infoMessage = "initDb: closed connection to database"
            Loghelper.logInfo(infoMessage)

    # Tabelle SubmissionResult anlegen
    sqlCommand = """
    CREATE TABLE IF NOT EXISTS SubmissionResult (
     Id integer PRIMARY KEY AUTOINCREMENT,
     GradeRunId integer NOT NULL,
     SubmissionId integer NOT NULL,
     Exercise text NOT NULL,
     Semester text NOT NULL,
     Module text NOT NULL,
     GradePoints integer,
     GradeErrors integer
    );
    """
    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.execute(sqlCommand)
        infoMessage = f"initDb: created table SubmissionResult"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"initDb: error creating table SubmissionResult ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()
            infoMessage = "initDb: closed connection to database"
            Loghelper.logInfo(infoMessage)

    # Tabelle Student anlegen
    sqlCommand = """
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
        dbCon.execute(sqlCommand)
        infoMessage = f"initDb: created table Student"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"initDb: error creating Table Student ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()
            infoMessage = "initDb: closed connection to database"
            Loghelper.logInfo(infoMessage)

    # Tabelle Roster anlegen
    sqlCommand = """
    CREATE TABLE IF NOT EXISTS Roster (
     StudentId integer PRIMARY KEY,
     Semester text,
     Module text,
     Exercises text,
     Completed text
    );
    """
    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.execute(sqlCommand)
        infoMessage = f"initDb: created table Roster"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"initDb: error creating table Roster ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()
            infoMessage = "initDb: closed connection to database"
            Loghelper.logInfo(infoMessage)

'''
Stores a grade run 
'''
def storeGradeRun(dbPath, timestamp, semester, module, operator, submissionCount, okCount, errorCount):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"storeGradeRun: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return

    sqlCommand = "Insert Into GradeRun (Timestamp,Semester,Module, Operator,SubmissionCount,"
    sqlCommand += f"OKCount,ErrorCount) Values('{timestamp}','{semester}','{module}','{operator}',"
    sqlCommand += f"{submissionCount},{okCount},{errorCount})"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlCommand)
        dbCon.commit()
        infoMessage = f"storeGradeRun: Inserted row into table GradeRun (id={dbCur.lastrowid})"
        Loghelper.logInfo(infoMessage)
        # return the id of the new record
        return dbCur.lastrowid
    except Error as ex:
        infoMessage = f"storeGradeRun: error inserting row into Table GradeRun ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

'''
Stores a single submission of a student
'''
def storeSubmission(dbPath, timestamp, semester, module, exercise, studentId, files, path, complete) -> int:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"storeSubmission: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return -1

    sqlCommand = "Insert Into Submission (Timestamp,Semester,Module,Exercise,StudentId,Files,Path,Complete) "
    sqlCommand += f"Values('{timestamp}','{semester}','{module}','{exercise}',"
    sqlCommand += f"'{studentId}','{files}','{path}','{complete}')"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlCommand)
        dbCon.commit()
        infoMessage = f"storeSubmission: row inserted into Submission table (id={dbCur.lastrowid})"
        Loghelper.logInfo(infoMessage)
        # return the id of the new record
        return dbCur.lastrowid
    except Error as ex:
        infoMessage = f"storeSubmission: error inserting in Submission table ({ex})"
        Loghelper.logError(infoMessage)
        return -1
    finally:
        if dbCon != None:
            dbCon.close()

'''
Clears all the submission
'''
def clearAllSubmission(dbPath):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"clearAllSubmission: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return

    sqlCommand = "Delete From Submission"
    try:
        dbCon.execute(sqlCommand)
        dbCon.commit()
        infoMessage = f"clearAllSubmission: all rows in Table Submission deleted"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"clearAllSubmissions: error deleting all rows in Table Submission ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

'''
Gets all submisssions
'''
def getSubmissions(dbPath) -> dict:
    dict = {}
    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.row_factory = sqlite3.Row
    except Error as ex:
        infoMessage = f"getSubmissions: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return dict

    # group by als Alternative?
    sqlCommand = "Select * From Submission"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand)
        rows = cur.fetchall()
        for row in rows:
            id = row["id"]
            semester = row["Semester"]
            module = row["Module"]
            exercise = row["exercise"]
            studentId = row["StudentId"]
            files = row["files"]
            dirPath = row["path"]
            complete = row["complete"]
            # returns Student object or None
            student = DBHelper.getStudentById(dbPath, studentId)
            if dict.get(exercise) == None:
                dict[exercise] = {}
            if dict[exercise].get(student) == None:
                dict[exercise][student] = []
            submission = Submission(id, studentId)
            submission.studentId = studentId
            submission.exercise = exercise
            submission.module = module
            submission.semester = semester
            submission.complete = complete
            # all the file names part of the submission
            submission.files = files
            # store the directory path of the files too
            submission.path = dirPath
            dict[exercise][student].append(submission)

    except Error as ex:
        infoMessage = f"getSubmissions: error querying Submission table ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

    return dict

'''
Gets all submissions by a student id
'''
def getSubmissionByStudentId(dbPath, studentId) -> [Submission]:
    submissions = []
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"getSubmissionByStudent: Error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return submissions

    sqlCommand = "Select * From Submission Where StudentId = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand, (studentId,))
        rows = cur.fetchall()
        for row in rows:
            submission = Submission(row[0])
            submission.studentId = row["studentId"]
            submissions.append(submission)
    except Error as ex:
        infoMessage = f"getSubmissionByStudentId: error querying Submission table ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

    return submissions

'''
Updates a single submission
'''
def updateSubmission(dbPath, submission) -> bool:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"updateSubmission: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return False

    id = submission.id
    complete = submission.complete
    sqlCommand = f"Update Submission Set Complete={complete} "
    sqlCommand += f"Where Id={id}"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlCommand)
        dbCon.commit()
        infoMessage = f"updateSubmission: Submission table with id={id} updated"
        Loghelper.logInfo(infoMessage)
        return True
    except Error as ex:
        infoMessage = f"updateSubmission: error updating a row in the Submission table ({ex})"
        Loghelper.logError(infoMessage)
        return False
    finally:
        if dbCon != None:
            dbCon.close()

'''
Get the maximum grading id
'''
def getNextGradeRunId(dbPath) -> int:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"getNextGradeRunId: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return -1
    sqlCommand = "Select Max(Id) From GradeRun"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand)
        row = cur.fetchone()
        gradeId = 1 if row[0] == None else row[0] + 1
        return gradeId
        infoMessage = f"getNextGradeRunId: new gradeId={gradeId}"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"getNextGradeRunId: error executing query ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

'''
Stores the grading for a single submission during a grade run
'''
def storeSubmissionResult(dbPath, gradeRunId, submissionId, exercise, semester, module, gradePoints, gradeErrors):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"storeSubmissionResult: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return

    sqlCommand = "Insert Into SubmissionResult (GradeRunId,SubmissionId,Exercise,Semester,Module,GradePoints,GradeErrors) "
    sqlCommand += f"Values({gradeRunId},'{submissionId}','{exercise}','{semester}','{module}',"
    sqlCommand += f"{gradePoints},{gradeErrors})"
    try:
        dbCur = dbCon.cursor()
        dbCur.execute(sqlCommand)
        dbCon.commit()
        infoMessage = f"storeSubmissionResult: row added to SubmissionResult table"
        Loghelper.logInfo(infoMessage)
    except Error as ex:
        infoMessage = f"storeSubmissionResult: error inserting a row to SubmissionResult table ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

'''
Gets all grade runs
'''
def getAllGradeRuns(dbPath):
    try:
        dbCon = sqlite3.connect(dbPath)
        dbCon.row_factory = sqlite3.Row
    except Error as ex:
        infoMessage = f"getAllGradeRuns: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return

    sqlCommand = "Select * From GradeRun"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand)
        rows = cur.fetchall()
        return rows
    except Error as ex:
        infoMessage = f"getAllGradeRuns: error querying GradeRun table ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

'''
Gets a grade run by id
'''
def getGradeRun(dbPath, runId):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"getGradeRun: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return

    sqlCommand = "Select * From GradeRun Where Id = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand, (runId,))
        row = cur.fetchone()
        if row == None:
            return 0
        else:
            return row[0]
    except Error as ex:
        infoMessage = f"getGradeRun: error querying GradeRun table ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

'''
Get all submission results
'''
def getAllSubmissionResult(dbPath):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"getAllSubmissionResult: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return

    sqlCommand = "Select * From SubmissionResult"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand)
        rows = cur.fetchall()
        return rows
    except Error as ex:
        infoMessage = f"getAllSubmissionResult: error querying SubmissionResult table ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

'''
Get all the submission results for a single student
'''
def getSubmissionResultByStudent(dbPath, student):
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"getSubmissionResultByStudent: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return

    sqlCommand = "Select * From SubmissionResult Where Student = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand, (student,))
        rows = cur.fetchall()
        return rows
    except Error as ex:
        infoMessage = f"getSubmissionResultByStudent: error querying submissionResult table ({ex})"
        Loghelper.logError(infoMessage)
        return None
    finally:
        if dbCon != None:
            dbCon.close()

'''
get a single student id by name - either first_last or first last
'''
def getStudentId(dbPath, studentName) -> int:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"getStudentId: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return -1

    # switch blank with _ if just in case
    studentName = studentName.replace(" ", "_")
    # name still valid?
    if len(studentName.split("_")) > 2:
        return -1

    firstName,lastName = studentName.split("_") if len(studentName.split("_")) == 2 else ("",studentName)

    if firstName == "":
        sqlCommand = "Select Id From Student Where Lastname = ?"
    else:
        sqlCommand = "Select Id From Student Where Firstname=? and Lastname = ?"
    try:
        cur = dbCon.cursor()
        if firstName == "":
            cur.execute(sqlCommand, (studentName,))
        else:
            cur.execute(sqlCommand, (firstName,lastName))
        row = cur.fetchone()
        if row != None:
            return row[0]
        else:
            infoMessage = f"getStudentId: no student id for {studentName}"
            Loghelper.logError(infoMessage)
            return -1
    except Error as ex:
        infoMessage = f"getStudentId: error querying Student table ({ex})"
        Loghelper.logError(infoMessage)
        return -1
    finally:
        if dbCon != None:
            dbCon.close()

'''
get a list of student ids by the last name only
'''
def searchStudentId(dbPath, studentName) -> []:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"searchStudentId: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return None

    sqlCommand = "Select Id From Student Where Lastname = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand, (studentName,))
        rows = cur.fetchall()
        studentIdList = [row[0] for row in rows]
        return studentIdList
    except Error as ex:
        infoMessage = f"searchStudentId: error querying Student table ({ex})"
        Loghelper.logError(infoMessage)
        return None
    finally:
        if dbCon != None:
            dbCon.close()

'''
get student name by id
'''
def getStudentById(dbPath, studentId) -> Student:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"getStudentById: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return

    sqlCommand = "Select FirstName,LastName,EMail From Student Where Id = ?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand, (studentId,))
        row = cur.fetchone()
        if row != None:
            student = Student(studentId)
            student.firstName = row[0]
            student.lastName = row[1]
            student.email = row[2]
            return student
        else:
            return None
    except Error as ex:
        infoMessage = f"getStudentById: error querying student table ({ex})"
        Loghelper.logError(infoMessage)
        return None
    finally:
        if dbCon != None:
            dbCon.close()

'''
stores a student
'''
def storeStudent(dbPath, studentId, studentName, studentEMail) -> int:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"storeStudent: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return -1

    # check if student id already exists
    sqlCommand = f"Select Id From Student Where Id=?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand, (studentId,))
        row = cur.fetchone()
        # any data?
        if row != None:
            # what data to return?
            infoMessage = f"storeStudent: student with id={row[0]} already exists"
            Loghelper.logInfo(infoMessage)
            return row[0]
    except Error as ex:
        infoMessage = f"storeStudent: error querying Student table ({ex})"
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
        sqlCommand = f"Insert Into Student (Id, FirstName, LastName, EMail, Remarks) "
        sqlCommand += f"Values ('{studentId}','{firstName}','{lastName}','{studentEMail}', '{remarks}')"
        dbCur = dbCon.cursor()
        dbCur.execute(sqlCommand)
        dbCon.commit()
        infoMessage = f"storeStudent: row inserted in Student table (id={dbCur.lastrowid})"
        Loghelper.logInfo(infoMessage)
        # return the id of the new record
        return dbCur.lastrowid
    except Error as ex:
        infoMessage = f"storeStudent: error inserting row into Student table ({ex})"
        Loghelper.logError(infoMessage)
        return -1
    finally:
        if dbCon != None:
            dbCon.close()

'''
stores a student roster 
'''
def storeRoster(dbPath, semester, module, studentId, exercises) -> int:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"storeRoster: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)

    # check if studentId already exists

    sqlCommand = f"Select StudentId From Roster Where StudentId=?"
    try:
        cur = dbCon.cursor()
        cur.execute(sqlCommand, (studentId,))
        row = cur.fetchone()
        # any data?
        if row != None:
            # what data to return?
            infoMessage = f"storeRoster: student with id={row[0]} already exists"
            Loghelper.logInfo(infoMessage)
            return studentId
    except Error as ex:
        infoMessage = f"storeRoster: error querying Roster table ({ex})"
        Loghelper.logError(infoMessage)
        return -1

    # now insert new roster with studentId
    try:
        # student id is always a number?
        studentId = int(studentId)
        # field completed contains false for every exercise
        completed = ",".join(["0" for _ in exercises.split(",")])
        sqlCommand = f"Insert Into Roster Values ({studentId},'{semester}','{module}','{exercises}','{completed}')"
        dbCur = dbCon.cursor()
        dbCur.execute(sqlCommand)
        dbCon.commit()
        infoMessage = f"storeRoster: row added to table Roster with id={dbCur.lastrowid}"
        Loghelper.logInfo(infoMessage)
        # return the id of the new record
        return dbCur.lastrowid
    except Error as ex:
        infoMessage = f"storeRoster: error inserting row into Roster table ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

'''
get the student roster 
'''
def getRoster(dbPath) -> []:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"getRoster: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)

    sqlCommand = f"Select * From Roster"

    rosters = []
    try:
        dbCon.row_factory = sqlite3.Row
        cur = dbCon.cursor()
        cur.execute(sqlCommand)
        rows = cur.fetchall()
        for row in rows:
            rowDict = dict([(k,row[k]) for k in row.keys()])
            rosters.append(Roster(**rowDict))
        return rosters
    except Error as ex:
        infoMessage = f"storeRoster: error querying Roster table ({ex})"
        Loghelper.logError(infoMessage)
    finally:
        if dbCon != None:
            dbCon.close()

'''
update the student roster with the submitted exercise
'''
def updateRoster(dbPath, studentId, exercise) -> bool:
    try:
        dbCon = sqlite3.connect(dbPath)
    except Error as ex:
        infoMessage = f"updateRoster: error connecting to database ({ex})"
        Loghelper.logError(infoMessage)
        return False

    # get the current value of exercises and completed
    try:
        sqlCommand = "Select Exercises, Completed From Roster Where StudentId=?"
        cur = dbCon.cursor()
        cur.execute(sqlCommand, (studentId,))
        row = cur.fetchone()
        # any data?
        if row == None:
            infoMessage = f"udpateRoster: no roster entry for studentId={studentId}"
            Loghelper.logError(infoMessage)
            return
        exercisesStudent = row[0]
        completed = row[1]
    except Error as ex:
        infoMessage = f"udpateRoster: error querying Roster table ({ex})"
        Loghelper.logError(infoMessage)
        return False

    # update the exercises for the student
    exercisesStudList = exercisesStudent.split(",")
    completedList = completed.split(",")

    # get the index of the exercise in the list
    exerciseIndex = exercisesStudList.index(exercise) if exercise in exercisesStudList else None

    if exerciseIndex == None:
        infoMessage = f"udpateRoster: exercise {exercise} not found in exercises for student {studentId}"
        Loghelper.logError(infoMessage)
        return False
    else:

        # set the index in the completed list to 1
        completedList[exerciseIndex] = "1"

        # get the new value for completed
        completed = ",".join(completedList)

        # update the completed exercises
        sqlCommand = f"Update Roster Set completed='{completed}' Where StudentId={studentId}"
        try:
            dbCur = dbCon.cursor()
            dbCur.execute(sqlCommand)
            dbCon.commit()
            infoMessage = f"updateRoster: updated table Roster"
            Loghelper.logInfo(infoMessage)
        except Error as ex:
            infoMessage = f"updateRoster: error updating table Roster ({ex})"
            Loghelper.logError(infoMessage)
            return False
        finally:
            if dbCon != None:
                dbCon.close()

    return True

