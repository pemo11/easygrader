# =============================================================================
# Automatisiertes Bewerten von Java-Programmieraufgaben
# Erstellt: 01/03/22
# Letztes Update: 03/03/22
# =============================================================================
import os
import re
import shutil
import tempfile

import loghelper
from GradeReport import GradeReport
from GradeAction import GradeAction
from XmlHelper import XmlHelper

# Globale Variablen
taskBasePath = "E:\\Graja-Testpool\\Java1"
submissionPath = "E:\\Graja-Testpool\\Einsendeaufgaben"

'''
Main starting point
'''
def start():
    # Create temp directory for all temp files
    tempPath = os.path.join(tempfile.gettempdir(), "simplegrader")
    if not os.path.exists(tempPath):
        os.mkdir(tempPath)
        infoMessage = f"{tempPath} wurde angelegt."
        loghelper.logInfo(infoMessage)
    # Initiate grading plan
    xmlHelper = XmlHelper("gradingplan.xml")
    # new GradeReport object for the output
    gradeReport = GradeReport()
    # List for all grading actions
    gradeActionList = []
    # go through all submissions
    for submission in os.listdir(submissionPath):
        taskName = submission
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
                # Create temp directory for studentId
                studentIdPath = os.path.join(tempPath, studentId)
                if not os.path.exists(studentIdPath):
                    os.mkdir(studentIdPath)
                # Get action for the task
                actionList = xmlHelper.getActionList(taskName, taskLevel)
                for action in actionList:
                    infoMessage = f"Executing Action {action.command} for file {javaFile}"
                    loghelper.logInfo(infoMessage)
                    if action.type == "compile":
                        gradeAction = GradeAction("compile")
                        gradeAction.result = "OK"
                        gradeActionList.append(gradeAction)
                # Get all the tests for the task
                testList = xmlHelper.getTestList(taskName, taskLevel)
                for test in testList:
                    infoMessage = f"Executing test {test.name} for file {javaFile}"
                    loghelper.logInfo(infoMessage)
                    gradeAction = GradeAction("test")
                    gradeAction.result = "OK"
                    gradeActionList.append(gradeAction)

            # Write XML-Report
            xmlHelper.generateGradingReport(gradeActionList)

# Starting point
if __name__ == "__main__":
    start()

