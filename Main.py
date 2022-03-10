# =============================================================================
# Automatisiertes Bewerten von Java-Programmieraufgaben
# Erstellt: 01/03/22
# Letztes Update: 10/03/22
# Version 0.2
# =============================================================================
import datetime
import os
import re
import shutil
import tempfile
import configparser
import subprocess

import ZipHelper
import Loghelper
from GradeReport import GradeReport
from GradeAction import GradeAction
from Submission import Submission
from XmlHelper import XmlHelper
import JavaHelper
import DBHelper

# Globale Variablen
appVersion = "0.2"
taskBasePath = ""
submissionPath = ""
dbPath = ""
gradingPlan = ""
gradeModule = ""
gradeExercise = ""
gradeSemester = ""
gradingOperator = ""

'''
get values for global variables from ini file
'''
def initVariables():
    global taskBasePath, submissionPath, dbPath
    global gradingPlan, gradeModule, gradeExercise, gradeSemester, gradingOperator
    config = configparser.ConfigParser()
    config.read("Simpleparser.ini")
    taskBasePath = config["path"]["taskBasePath"]
    submissionPath = config["path"]["submissionPath"]
    dbPath = config["path"]["dbPath"]
    gradingPlan = config["run"]["gradingplan"]
    gradeModule = config["run"]["gradeModule"]
    gradeExercise = config["run"]["gradeExercise"]
    gradeSemester = config["run"]["gradeSemester"]
    gradingOperator = config["run"]["gradingOperator"]

'''
Shows application main menue
'''
def showMenu():
    menuList = []
    menuList.append("Alle Abgaben anzeigen")
    menuList.append("Alle Abgaben graden")
    menuList.append("Grading-Runs anzeigen")
    menuList.append("Abgaben eines Studenten anzeigen")
    menuList.append("Gradings eines Studenten anzeigen")
    prompt = "Eingabe ("
    print("*" * 80)
    print(f"{'*' * 24}{f' Welcome to Simple Grader {appVersion} '}{'*' * 25}")
    print("*" * 80)
    for i, menuItem in enumerate(menuList):
        print(f"{chr(i+65)}) {menuItem}")
        prompt += f"{chr(i+65)},"
    print("Q) Ende")
    prompt = prompt[:-1] + " oder Q fuer Ende)?\n"
    return input(prompt)

'''
Assumes each submission file name:
EA1_A_PMonadjemi.zip
EA1_B_PMonadjemi.zip
or
EA1_PMonadjemi.zip
in this case default level is assumed
'''
def getSubmissionFilesMethodA(submissionPath):
    submissionList = []
    subnamePattern1 = "(?P<task>\w+)_Level(?P<level>\w)_(?P<student>[_\w]+)\.zip"
    # Der "Trick des Jahres" - non greedy dank *? anstelle von +, damit der Vorname nicht dem Aufgabenname zugeordnet wird
    subnamePattern2 = "(?P<task>\w*?)_(?P<student>[_\w]+)\.zip"
    for i, submissionFile in enumerate([fi for fi in os.listdir(submissionPath) if fi.endswith(".zip")]):
        # import: finditer instead of findall because of the named capture groups
        nameElements = list(re.finditer(subnamePattern1, submissionFile))
        if (len(nameElements) == 0):
            nameElements = list(re.finditer(subnamePattern2, submissionFile))
        id = f"{i+1:03d}"
        excercise = nameElements[0].group("task")
        student = nameElements[0].group("student")
        level = nameElements[0].group("level") if len(nameElements) == 3 else "A"
        submission = Submission(id, student)
        submission.zipPath = os.path.join(submissionPath, submissionFile)
        submission.exercise = excercise
        submission.level = level
        submission.semester = os.path.basename(submissionFile)
        submissionList.append(submission)
    return submissionList

'''
Assumes a directory hierarchy
not in used at the moment
EA1
 -LevelA
  --EA1_A_PMonadjemi.java
  --EA1_Tester.java
'''
def getSubmissionFilesMethodB(submissionPath):
    for dirTuple in os.walk(submissionPath):
        # do java files exists?
        javaFiles = [f for f in dirTuple[2] if f.endswith("java")]
        if len(javaFiles) > 0:
            print(f">Scanning {dirTuple[0]}")
            level = os.path.basename(dirTuple[0])
            task = os.path.dirname(dirTuple[0])
            for javaFile in javaFiles:
                javaFilePath = os.path.join(dirTuple[0], javaFile)
                fileTimestamp = os.path.getatime(javaFilePath)
                lastAccessTime = datetime.datetime.fromtimestamp(fileTimestamp)
                print(f"task={task} level={level} file={javaFile} Last Access={lastAccessTime}")

'''
Show all submissions
'''
def showSubmissions():
    submissions = getSubmissions()
    for submission in submissions:
        print(submission)

'''
Get all submissions
'''
def getSubmissions():
    submissions = getSubmissionFilesMethodA(submissionPath)
    return submissions

'''
Get all grade runs
'''
def getGradeRuns():
    # returns tuples
    gradeRuns = DBHelper.getGradeRuns(dbPath)
    print("*" * 80)
    for gradeRun in gradeRuns:
        print(f"Id:{gradeRun[0]} Timestamp:{gradeRun[1]} Semester:{gradeRun[2]} Submission-Count:{gradeRun[3]}"
              f" OK-Count:{gradeRun[4]} ErrorCount:{gradeRun[5]}")
    print("*" * 80)
    print()

'''
Get all the submissions by a student name
'''
def getStudentSubmissions():
    studentName = input("Name des Studenten?")
    rows = DBHelper.getStudentSubmissions(dbPath, studentName)
    for row in rows:
        print(row[0])

'''
Get all the gradings by student name
'''
def getGradingsByStudent():
    studentName = input("Name des Studenten?")
    pass

'''
Start a grading run
'''
def startGradingRun():
    # Initiate grading plan
    xmlHelper = XmlHelper(gradingPlan)
    # new GradeReport object for the output
    gradeReport = GradeReport()
    # List for all grading actions
    gradeActionList = []
    # Create temp directory for all submissions
    tmpDirName = f"{gradeModule}_{gradeExercise}"
    tmpDirPath = os.path.join(tempfile.gettempdir(), tmpDirName)
    if not os.path.exists(tmpDirPath):
        os.mkdir(tmpDirPath)
        infoMessage = f"{tmpDirPath} created"
        Loghelper.logInfo(infoMessage)
    # go through all submissions
    submissions = getSubmissions()
    print(f"*** Start grading the submissions in {submissionPath} ***")
    for submission in submissions:
        taskName = submission.exercise
        taskLevel = submission.level
        studentName = submission.student
        zipPath = submission.zipPath
        # archivePath = os.path.join(submissionPath, student)
        # if not os.path.exists(archivePath):
        #     os.mkdir(archivePath)
        #     infoMessage = f"{archivePath} created"
        #     loghelper.logInfo(infoMessage)
        # Expand archive and the path back
        archivePath = ZipHelper.extractZip(tmpDirPath, zipPath)
        archiveName = os.path.basename(archivePath)

        # go through all submitted files in the archive directory
        javaFiles = [fi for fi in os.listdir(archivePath) if fi.endswith(".java")]
        for javaFile in javaFiles:
            # Get action for the task
            actionList = xmlHelper.getActionList(taskName, taskLevel)
            for action in actionList:
                if not eval(action.active):
                    infoMessage = f"Leaving out Action {action.command} for {javaFile}"
                    Loghelper.logInfo(infoMessage)
                    continue
                infoMessage = f"Executing Action {action.command} for {javaFile}/StudentId: {studentName}"
                Loghelper.logInfo(infoMessage)
                if action.type == "java-compile":
                    gradeAction = GradeAction("Java compile")
                    gradeAction.student = studentName
                    # Wird dieses Attribut benötigt?
                    gradeAction.submission = f"Submission for {studentName}"
                    gradeAction.description = f"Compiling {javaFile}"
                    javaFilePath = os.path.join(archivePath, javaFile)
                    compileResult = JavaHelper.compileJava(javaFilePath)
                    gradePoints = 1 if compileResult[0] == 0 else 0
                    gradeAction.points = gradePoints
                    gradeAction.errorMessage = compileResult[1]
                    # Muss noch genauer definiert werden
                    actionSuccess = gradePoints > 0
                    gradeAction.success = actionSuccess
                    gradeActionList.append(gradeAction)
            # Get all the tests for the task
            testList = xmlHelper.getTestList(taskName, taskLevel)
            for test in testList:
                if not eval(test.active):
                    infoMessage = f"Leaving out Test {test.name} for {javaFile}"
                    Loghelper.logInfo(infoMessage)
                    continue
                infoMessage = f"Executing test {test.name} for file {javaFile}"
                Loghelper.logInfo(infoMessage)
                gradeAction = GradeAction("test")
                gradeAction.submission = f"{submission}"
                gradeAction.description = f"Executing test {test.name}"
                if test.type == "JUNIT":
                    pass
                elif test.type == "Text-Compare":
                    pass
                else:
                    infoMessage = f"{test.type} ist ein unbekannter Testtyp"
                    Loghelper.logInfo(infoMessage)
                # TODO: Natürlich nur provisorisch
                gradeAction.result = "OK"
                gradeAction.success = True
                gradeActionList.append(gradeAction)

    # Store grade run in the database
    timestamp = datetime.datetime.now()
    okCount = len([gr for gr in gradeActionList if gr.success])
    errorCount = len([gr for gr in gradeActionList if not gr.success])
    gradeRunId = DBHelper.storeGradeRun(dbPath, timestamp, gradeSemester, gradingOperator, len(submissions), okCount, errorCount)

    # Store all submissions
    for submission in submissions:
        DBHelper.storeSubmission(dbPath, gradeRunId, submission.student)

    # Write XML-Report
    reportPath = xmlHelper.generateGradingReport(gradeActionList)
    # display report file
    subprocess.call(["notepad.exe", reportPath])

    htmlPath = xmlHelper.generateHtmlReport(reportPath, gradeSemester, gradeModule, gradeExercise)
    os.startfile(htmlPath)
    print(f"{len(submissions)} Submissions bearbeitet - OK: {okCount} Error: {errorCount}")

'''
Main starting point
'''
def start():
    initVariables()
    infoMessage = f"Starting the mission (Version {appVersion}- executing {gradingPlan}"
    Loghelper.logInfo(infoMessage)
    # Create temp directory for all temp files
    tempPath = os.path.join(tempfile.gettempdir(), "simplegrader")
    if not os.path.exists(tempPath):
        os.mkdir(tempPath)
        infoMessage = f"{tempPath} wurde angelegt."
        Loghelper.logInfo(infoMessage)
    # Create database
    if not os.path.exists(dbPath):
        DBHelper.initDb(dbPath)

    exitFlag = False
    while not exitFlag:
        choice = showMenu().upper()
        if choice == "Q":
            exitFlag = True
        elif choice == "A":
            showSubmissions()
        elif choice == "B":
            startGradingRun()
        elif choice == "C":
            getGradeRuns()
        elif choice == "D":
            getStudentSubmissions()
        elif choice == "E":
            getStudentGradings()
        else:
            print(f"!!! {choice} ist eine relativ unbekannte Auswahl !!!")

# Starting point
if __name__ == "__main__":
    start()

