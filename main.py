# =============================================================================
# Automatisiertes Bewerten von Java-Programmieraufgaben
# Erstellt: 01/03/22
# Letztes Update: 04/03/22
# =============================================================================
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

def initVariables():
    global taskBasePath, submissionPath, gradingPlan
    config = configparser.ConfigParser()
    config.read("simpleparser.ini")
    taskBasePath = config["path"]["taskBasePath"]
    submissionPath = config["path"]["submissionPath"]
    gradingPlan = config["path"]["gradingplan"]

'''
Main starting point
'''
def start():
    global submissionCount
    initVariables()
    infoMessage = f"Starting the mission - executing {gradingPlan}"
    loghelper.logInfo(infoMessage)
    # Create temp directory for all temp files
    tempPath = os.path.join(tempfile.gettempdir(), "simplegrader")
    if not os.path.exists(tempPath):
        os.mkdir(tempPath)
        infoMessage = f"{tempPath} wurde angelegt."
        loghelper.logInfo(infoMessage)
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

# Starting point
if __name__ == "__main__":
    start()

