# =============================================================================
# Automatisiertes Bewerten von Java-Programmieraufgaben
# Erstellt: 01/03/22
# Letztes Update: 08/03/22
# Version 0.12
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

# Globale Variablen
appVersion = "0.12"
taskBasePath = ""
submissionPath = ""
gradingPlan = ""
gradeModule = ""
gradeExercise = ""

'''
get values for global variables from ini file
'''
def initVariables():
    global taskBasePath, submissionPath, gradingPlan, gradeModule, gradeExercise
    config = configparser.ConfigParser()
    config.read("Simpleparser.ini")
    taskBasePath = config["path"]["taskBasePath"]
    submissionPath = config["path"]["submissionPath"]
    gradingPlan = config["run"]["gradingplan"]
    gradeModule = config["run"]["gradeModule"]
    gradeExercise = config["run"]["gradeExercise"]

'''
Shows application main menue
'''
def showMenu():
    menuList = []
    menuList.append("Alle Abgaben anzeigen")
    menuList.append("Alle Abgaben graden")
    prompt = "Eingabe ("
    print("*" * 80)
    print(f"{'*' * 24}{' Welcome to Simple Grader v0.1 '}{'*' * 25}")
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
                    gradeAction.result = compileResult
                    gradeAction.success = compileResult == 0
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
                # TODO: Natürlich nur provisorisch
                gradeAction.result = "OK"
                gradeAction.success = True
                gradeActionList.append(gradeAction)

    # Write XML-Report
    reportPath = xmlHelper.generateGradingReport(gradeActionList)
    # display report file
    subprocess.call(["notepad.exe", reportPath])

    htmlPath = xmlHelper.generateHtmlReport(reportPath)
    os.startfile(htmlPath)

    print(f"{len(submissions)} Submissions bearbeitet")


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
    exitFlag = False
    while not exitFlag:
        choice = showMenu().upper()
        if choice == "Q":
            exitFlag = True
        elif choice == "A":
            showSubmissions()
        elif choice == "B":
            startGradingRun()
        else:
            print(f"!!! {choice} ist eine unbekannte Auswahl !!!")

# Starting point
if __name__ == "__main__":
    start()

