# =============================================================================
# Automatisiertes Bewerten von Java-Programmieraufgaben
# Erstellt: 01/03/22
# Letztes Update: 04/03/22
# Version 0.1
# =============================================================================
import datetime
import os
import re
import shutil
import tempfile
import configparser

import loghelper
from GradeReport import GradeReport
from GradeAction import GradeAction
from XmlHelper import XmlHelper
import JavaHelper

# Globale Variablen
submissionCount = 0
appVersion = "0.1"

def initVariables():
    global taskBasePath, submissionPath, gradingPlan
    config = configparser.ConfigParser()
    config.read("simpleparser.ini")
    taskBasePath = config["path"]["taskBasePath"]
    submissionPath = config["path"]["submissionPath"]
    gradingPlan = config["path"]["gradingplan"]

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
    prompt = prompt[:-1] + " oder Q fuer Ende)?"
    return input(prompt)

'''
Show all submissions
'''
def showSubmissions():
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
Start a grading run
'''
def startGradingRun():
    global submissionCount
    # Initiate grading plan
    xmlHelper = XmlHelper(gradingPlan)
    # new GradeReport object for the output
    gradeReport = GradeReport()
    # List for all grading actions
    gradeActionList = []
    # go through all submissions
    for submission in os.listdir(submissionPath):
        taskName = submission
        submissionCount += 1
        taskPath = os.path.join(submissionPath, taskName)
        # List all levels in the submission directory
        for level in os.listdir(taskPath):
            taskLevel = level
            levelPath = os.path.join(taskPath, level)
            # go through all submitted files
            javaFiles = [fi for fi in os.listdir(levelPath) if fi.endswith(".java")]
            for javaFile in javaFiles:
                pattern = "(\d+)_App.java"
                studentId = re.findall(pattern, javaFile)[0]
                # Get action for the task
                actionList = xmlHelper.getActionList(taskName, taskLevel)
                for action in actionList:
                    if not eval(action.active):
                        infoMessage = f"Leaving out Action {action.command} for {javaFile}"
                        loghelper.logInfo(infoMessage)
                        continue
                    infoMessage = f"Executing Action {action.command} for {javaFile}/StudentId: {studentId}"
                    loghelper.logInfo(infoMessage)
                    if action.type == "compile":
                        gradeAction = GradeAction("compile")
                        gradeAction.description = f"Compiling {javaFile}"
                        javaFilePath = os.path.join(levelPath, javaFile)
                        compileResult = JavaHelper.compileJava(javaFilePath)
                        gradeAction.result = compileResult
                        gradeActionList.append(gradeAction)
                # Get all the tests for the task
                testList = xmlHelper.getTestList(taskName, taskLevel)
                for test in testList:
                    if not eval(test.active):
                        infoMessage = f"Leaving out Test {test.name} for {javaFile}"
                        loghelper.logInfo(infoMessage)
                        continue
                    infoMessage = f"Executing test {test.name} for file {javaFile}"
                    loghelper.logInfo(infoMessage)
                    gradeAction = GradeAction("test")
                    gradeAction.description = f"Executing test {test.name}"
                    gradeAction.result = "OK"
                    gradeActionList.append(gradeAction)

            # Write XML-Report
            xmlHelper.generateGradingReport(gradeActionList)

        print(f"{submissionCount} Submissions berbeitet")

'''
Main starting point
'''
def start():
    initVariables()
    infoMessage = f"Starting the mission (Version {appVersion}- executing {gradingPlan}"
    loghelper.logInfo(infoMessage)
    # Create temp directory for all temp files
    tempPath = os.path.join(tempfile.gettempdir(), "simplegrader")
    if not os.path.exists(tempPath):
        os.mkdir(tempPath)
        infoMessage = f"{tempPath} wurde angelegt."
        loghelper.logInfo(infoMessage)
    exitFlag = False
    while not exitFlag:
        choice = showMenu()
        print(choice)
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

