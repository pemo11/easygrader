# =============================================================================
# Automatisiertes Bewerten von Java-Programmieraufgaben
# Erstellt: 01/03/22
# Letztes Update: 13/03/22
# Version 0.32
# =============================================================================
import datetime
import os
import re
import shutil
import tempfile
import configparser
import subprocess
import csv

import ZipHelper
import Loghelper
from GradeReport import GradeReport
from GradeAction import GradeAction
from GradeResult import GradeResult
from Submission import Submission
from XmlHelper import XmlHelper
import JavaHelper
import DBHelper

# Globale Variablen
appVersion = "0.32"
taskBasePath = ""
submissionPath = ""
gradingPlanPath = ""
studentRosterPath = ""
dbPath = ""
gradeModule = ""
gradeExercise = ""
gradeSemester = ""
gradingOperator = ""

'''
get values for global variables from ini file
'''
def initVariables():
    global taskBasePath, submissionPath, gradingPlanPath, studentRosterPath, dbPath
    global gradeModule, gradeExercise, gradeSemester, gradingOperator
    config = configparser.ConfigParser()
    config.read("Simpleparser.ini")
    taskBasePath = config["path"]["taskBasePath"]
    submissionPath = config["path"]["submissionPath"]
    gradingPlanPath = config["path"]["gradingPlanPath"]
    studentRosterPath = config["path"]["studentRosterPath"]
    dbPath = config["path"]["dbPath"]
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
    menuList.append("Alle Abgaben eines Studenten anzeigen")
    menuList.append("Grading-Run starten")
    menuList.append("Alle Grading-Runs anzeigen")
    menuList.append("Alle Gradings anzeigen")
    menuList.append("Alle Gradings eines Studenten anzeigen")
    menuList.append("Studenten ohne Abgaben anzeigen")
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
Gets a list of all submissions in a single (flat) directory
Assumes each submission file name:
EA1_A_PMonadjemi.zip
EA1_B_PMonadjemi.zip
or
EA1_PMonadjemi.zip
in this case default level A is assumed
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
        submission.module = gradeModule
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
Get all submissions
'''
def getSubmissions():
    submissions = getSubmissionFilesMethodA(submissionPath)
    return submissions

'''
Get all grade runs from the database
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
Get all student submissions from the submission directory
'''
def getStudentSubmissions():
    subnamePattern1 = "(?P<task>\w+)_Level(?P<level>\w)_(?P<student>[_\w]+)\.zip"
    # Der "Trick des Jahres" - non greedy dank *? anstelle von +, damit der Vorname nicht dem Aufgabenname zugeordnet wird
    subnamePattern2 = "(?P<task>\w*?)_(?P<student>[_\w]+)\.zip"
    submiDic = {}
    for submiFile in [f for f in os.listdir(submissionPath) if f.endswith(".zip")]:
        # import: finditer instead of findall because of the named capture groups
        nameElements = list(re.finditer(subnamePattern1, submiFile))
        if (len(nameElements) == 0):
            nameElements = list(re.finditer(subnamePattern2, submiFile))
        student = nameElements[0].group("student")
        exercise = nameElements[0].group("task")
        level = nameElements[0].group("level") if len(nameElements) == 3 else "A"
        # print(f"Submission from {student} for {exercise} (Level {level})")
        # Already entry in the dic?
        if submiDic.get(student) == None:
            submiDic[student] = [exercise]
        else:
            submiDic[student].append(exercise)
    return submiDic

'''
Outputs all student submissions
'''
def showSubmissions():
    dic = getStudentSubmissions()
    # go through all entries
    for student in dic:
        print(f"Submissions by {student}")
        for exercise in dic[student]:
            print(f">> {exercise}")

'''
Get all submissions for a student by name 
'''
def showSubmissionsByStudent():
    studentName = input("Name des Studenten?")
    # Name etwas aufbereiten, da die Namen als Vorname_Nachname abgelegt sind
    studentName = studentName.replace(" ", "_")
    dic = getStudentSubmissions()
    if dic.get(studentName):
        print(f"Submissions by {studentName}")
        for exercise in dic[studentName]:
            print(f">> {exercise}")
    else:
        print(f"Keine Submissions by {studentName}")
        # TODO: Später auch alternative Namen anzeigen

'''
Shows all gradings from the database
'''
def showGradings():
    rows = DBHelper.getSubmissionResults(dbPath)
    if rows != None and len(rows) > 0:
        for row in rows:
            print(row[0])

'''
Get all the gradings by student name from the database
'''
def showGradingsByStudent():
    studentName = input("Name des Studenten?")
    rows = DBHelper.getStudentSubmissionResults(dbPath, studentName)
    if rows != None and len(rows) > 0:
        for row in rows:
            print(row[0])
    else:
        print(f"*** Keine Gradings für {studentName} in der Datenbank ***")

'''
Gets the content of the roster file (CSV)
'''
def getStudentRoster(rosterPath):
    dic = {}
    with open(rosterPath, encoding="utf-8") as fh:
        csvReader = csv.reader(fh)
        next(fh)
        for row in csvReader:
            name = row[0].replace(" ", "_")
            # dic[row[0]] = row[1:-1]
            dic[name] = row[1:-1]
    return dic

'''
Shows all students without submissions for single assigments
'''
def showStudentsWithoutSubmission(csvPath):
    dicSubmissions = getStudentSubmissions()
    dicRoster = getStudentRoster(csvPath)
    for student in dicRoster:
        studentName = student.replace("_", " ")
        if dicSubmissions.get(student) == None:
            print(f"*** Keine Submissions von {studentName} ***")
        else:
            submissions = [s for s in dicRoster[student] if s == "1"]
            print(f"*** Student {studentName} {len(submissions)} von {len(dicSubmissions[student])} bewertet")
'''
Start a grading run
'''
def startGradingRun():
    # Initiate grading plan
    xmlHelper = XmlHelper(gradingPlanPath)
    # new GradeReport object for the output
    # gradeReport = GradeReport()
    # List for all grading actions for the grading Action report
    gradeActionList = []
    # List for all grading results for the grading Result report
    gradeResultList = []
    # Create temp directory for all submissions
    tmpDirName = f"{gradeModule}_{gradeExercise}"
    tmpDirPath = os.path.join(tempfile.gettempdir(), tmpDirName)
    # if the directory not exists it will be created
    if not os.path.exists(tmpDirPath):
        os.mkdir(tmpDirPath)
        infoMessage = f"directory {tmpDirPath} created"
        Loghelper.logInfo(infoMessage)
    # get all Submissions from the file system
    submissions = getSubmissions()
    # for the grading run duration
    startTime = datetime.datetime.now()
    print(f"*** Start grading the submissions in {submissionPath} ***")
    # go through all submissions
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
        # archiveName = os.path.basename(archivePath)

        # go through all submitted files in the archive directory
        javaFiles = [fi for fi in os.listdir(archivePath) if fi.endswith(".java")]
        for javaFile in javaFiles:
            # Get all actions for the task and level from the xml file
            actionList = xmlHelper.getActionList(taskName, taskLevel)
            # Go through all the actions
            for action in actionList:
                # skip not active actions
                if not eval(action.active):
                    infoMessage = f"Leaving out Action {action.command} for {javaFile}"
                    Loghelper.logInfo(infoMessage)
                    continue
                # Execute the action
                infoMessage = f"Executing Action {action.command} for {javaFile}/StudentId: {studentName}"
                Loghelper.logInfo(infoMessage)
                # the action depends on the action type
                if action.type == "java-compile":
                    # a new item for the action report
                    gradeAction = GradeAction("Java compile", "compile")
                    gradeAction.student = submission.student
                    gradeAction.fileName = javaFile
                    gradeActionList.append(gradeAction)
                    # a new item for the grade result report
                    gradeResult = GradeResult("Java compile")
                    gradeResult.student = studentName
                    # Wird dieses Attribut benötigt?
                    gradeResult.submission = f"Submission for {studentName}"
                    gradeResult.description = f"Compiling {javaFile}"
                    javaFilePath = os.path.join(archivePath, javaFile)
                    compileResult = JavaHelper.compileJava(javaFilePath)
                    gradePoints = 1 if compileResult[0] == 0 else 0
                    gradeResult.points = gradePoints
                    gradeResult.errorMessage = compileResult[1]
                    # Muss noch genauer definiert werden
                    actionSuccess = gradePoints > 0
                    gradeResult.success = actionSuccess
                    gradeResultList.append(gradeResult)

            # Get all the tests for the task
            testList = xmlHelper.getTestList(taskName, taskLevel)
            for test in testList:
                if not eval(test.active):
                    infoMessage = f"Leaving out Test {test.name} for {javaFile}"
                    Loghelper.logInfo(infoMessage)
                    continue
                infoMessage = f"Executing test {test.name} for file {javaFile}"
                Loghelper.logInfo(infoMessage)

                gradeAction = GradeAction(test.type, "test")
                gradeAction.student = submission.student
                gradeAction.javaFile = javaFile
                gradeActionList.append(gradeAction)

                gradeResult = GradeResult(f"{test.type}-Test")
                gradeResult.submission = f"{submission}"
                gradeResult.description = f"Executing test {test.name}"
                if test.type == "JUnit":
                    pass
                elif test.type == "Text-Compare":
                    pass
                else:
                    infoMessage = f"{test.type} ist ein unbekannter Testtyp"
                    Loghelper.logInfo(infoMessage)
                # TODO: Natürlich nur provisorisch
                gradeResult.result = "OK"
                gradeResult.success = True
                gradeResultList.append(gradeResult)

    # Store grade run in the database
    timestamp = datetime.datetime.now()
    okCount = len([gr for gr in gradeResultList if gr.success])
    errorCount = len([gr for gr in gradeResultList if not gr.success])
    gradeRunId = DBHelper.storeGradeRun(dbPath, timestamp, gradeSemester, gradeModule, gradingOperator, len(submissions), okCount, errorCount)

    # Store all submissions in the database
    for submission in submissions:
        # ResultPoints und Remarks müssen noch eingefügt werden
        DBHelper.storeSubmissionResult(dbPath, gradeRunId, submission.student, submission.exercise,
                                       submission.level, submission.semester, submission.module,
                                       submission.fileName, 0, "Keine")

    # Write XML-Reports
    actionReportPath = xmlHelper.generateActionReport(gradeActionList)
    # display report file
    subprocess.call(["notepad.exe", actionReportPath])

    gradeReportPath = xmlHelper.generateGradingReport(gradeResultList)
    # display report file
    subprocess.call(["notepad.exe", gradeReportPath])

    htmlPath = xmlHelper.generateHtmlReport(gradeReportPath, gradeSemester, gradeModule, gradeExercise)
    os.startfile(htmlPath)
    print(f"{len(submissions)} Submissions bearbeitet - OK: {okCount} Error: {errorCount}")

'''
Main starting point
'''
def start():
    initVariables()
    infoMessage = f"Starting the mission (Version {appVersion}- executing {gradingPlanPath}"
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
            showSubmissionsByStudent()
        elif choice == "C":
            startGradingRun()
        elif choice == "D":
            getGradeRuns()
        elif choice == "E":
            showGradings()
        elif choice == "F":
            showGradingsByStudent()
        elif choice == "G":
            showStudentsWithoutSubmission(studentRosterPath)
        else:
            print(f"!!! {choice} ist eine relativ unbekannte Auswahl !!!")

# Starting point
if __name__ == "__main__":
    start()

