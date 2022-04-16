# =============================================================================
# Automatisiertes Bewerten von Java-Programmieraufgaben
# Erstellt: 01/03/22
# Letztes Update: 16/04/22
# Version 0.5
# =============================================================================
import datetime
import os
import re
import shutil
import tempfile
import configparser
import subprocess
import csv
import colorama
from colorama import Fore, Back, Style
import ZipHelper
import Loghelper

from GradeAction import GradeAction
from GradeResult import GradeResult
from Submission import Submission
from SubmissionFile import SubmissionFile
import RosterHelper
from XmlHelper import XmlHelper
import JavaRunHelper
import DBHelper

# =============================================================================
# Globale Variablen
# =============================================================================
appVersion = "0.50"
appName = "SimpelGrader"
taskBasePath = ""
submissionPath = ""
# this path contains the expanded files
submissionDestPath = ""
gradingPlanPath = ""
studentRosterPath = ""
submissionDic = None
dbPath = ""
gradeModule = ""
gradeSemester = ""
gradingOperator = ""
deleteSubmissionTree = False

# =============================================================================
# Initialization
# =============================================================================

'''
get values for global variables from ini file
'''
def initVariables():
    global taskBasePath, submissionPath, gradingPlanPath, studentRosterPath, dbPath, submissionDestPath
    global gradeModule, gradeSemester, gradingOperator, deleteSubmissionTree
    config = configparser.ConfigParser()
    config.read("Simpelgrader.ini")
    taskBasePath = config["path"]["taskBasePath"]
    submissionPath = config["path"]["submissionPath"]
    gradingPlanPath = config["path"]["gradingPlanPath"]
    studentRosterPath = config["path"]["studentRosterPath"]
    dbPath = config["path"]["dbPath"]
    gradeModule = config["run"]["gradeModule"]
    gradeSemester = config["run"]["gradeSemester"]
    gradeSemester = gradeSemester.replace(" ", "")
    gradeSemester = gradeSemester.replace("/", "_")
    gradingOperator = config["run"]["gradingOperator"]
    submissionDestPath = os.path.join(tempfile.gettempdir(), appName, gradeSemester, gradeModule)
    # Delete the directory if it already exists
    deleteSubmissionTree =  config["start"]["deleteSubmissionTree"]
    if not deleteSubmissionTree.upper().startswith("Y") and os.path.exists(submissionDestPath):
        shutil.rmtree(submissionDestPath)
        infoMessage = f"Verzeichnis {submissionDestPath} wurde mit seinem Inhalt entfernt."
        Loghelper.logInfo(infoMessage)
    if not os.path.exists(submissionDestPath):
        # create directory with all the subdirectories
        os.makedirs(submissionDestPath)
        infoMessage = f"Verzeichnis {submissionDestPath} wurde angelegt."
        Loghelper.logInfo(infoMessage)

# =============================================================================
# Helper functions
# =============================================================================

'''
Shows the Welcome Banner
'''
def showBanner():
    print(Fore.LIGHTGREEN_EX + "*" * 80)
    print(f"{'*' * 24}{f' Welcome to {appName} {appVersion} '}{'*' * 25}")
    print("*" * 80 + Style.RESET_ALL)

'''
Shows application main menue
'''
def showMenu():
    menuList = []
    menuList.append("Alle Abgaben einlesen")
    menuList.append("Alle Abgaben verarbeiten")
    menuList.append(Fore.LIGHTYELLOW_EX + "Bewertungsdurchlauf starten" + Style.RESET_ALL)
    menuList.append("Alle Bewertungsdurchläufe anzeigen")
    menuList.append("Alle Bewertungen eines Studenten anzeigen")
    print("=" * 80)
    prompt = "Eingabe ("
    for i, menuItem in enumerate(menuList):
        print(f"{chr(i+65)}) {menuItem}")
        prompt += f"{chr(i+65)},"
    print(Fore.LIGHTMAGENTA_EX + "Q) Ende" + Style.RESET_ALL)
    print("=" * 80)
    prompt = prompt[:-1] + " oder Q fuer Ende)?\n"
    return input(prompt)

# =============================================================================
# Main Menue functions
# =============================================================================

'''
Extracts all submission files downloaded from Moodle
This methods is always run first to make the submissions accessible for grading and 
other operations
Update: Its based on the fact that the Moodle download is a single zip file that contains
another submission zip file which finally contains the submitted zip file
the submission directory contains only one zip file, eg moodle_Submission_110422.zip
'''
def extractMoodleSubmissions() -> int:
    # extract zip file with all the submission zip files
    zipFiles = [fi for fi in os.listdir(submissionPath) if fi.endswith("zip")]
    # only one zip file allowed
    if len(zipFiles) != 1:
        infoMessage = f"extractSubmissions - exactly one zip file expected in {submissionPath}"
        Loghelper.logError(infoMessage)
        return False
    zipPath = os.path.join(submissionPath, zipFiles[0])
    # extract main submission zip
    ZipHelper.extractArchive(zipPath, submissionDestPath)
    # go through all extracted zip files and extract the moodle submission zip file
    for fiZip in [fi for fi in os.listdir(submissionDestPath) if fi.endswith("zip")]:
        fiPath = os.path.join(submissionDestPath, fiZip)
        ZipHelper.extractArchive(fiPath, submissionDestPath)
        # delete submission zip file in temp directory
        os.remove(fiPath)
    # check if every submission fits the name pattern eg. EA1A_Name1_Name2.zip
    filePattern = "(\w+)_(\w+)_(\w+)\.zip"
    fileErrorCount = 0
    fileCount = len(os.listdir(submissionDestPath))
    # check only files not directories if they match the name pattern for a submission zip file
    for fi in [f for f in os.listdir(submissionDestPath) if os.path.isfile(f)]:
        # does the filename matches the pattern?
        if not re.match(filePattern, fi):
            # move file to special directory
            rejectDirPath = os.path.join(submissionDestPath, "rejects")
            if not os.path.exists(rejectDirPath):
                os.mkdir(rejectDirPath)
                infoMessage = f"extractMoodleSubmissions: {rejectDirPath} directory created"
                Loghelper.logInfo(infoMessage)
            fileErrorCount += 1
            infoMessage = f"extractMoodleSubmissions: {fi} does not match name pattern"
            Loghelper.logError(infoMessage)
            # Move fi to the rejects directory
            filePath = os.path.join(submissionDestPath, fi)
            shutil.move(filePath, rejectDirPath)
            infoMessage = f"extractMoodleSubmissions: {filePath} moved to {rejectDirPath}"
            Loghelper.logInfo(infoMessage)
    if fileErrorCount > 0:
        infoMessage = f"extractMoodleSubmissions: {fileErrorCount} of {fileCount} does not match name pattern"
        Loghelper.logError(infoMessage)

    # go through all extracted submission files and extract all submitted files
    # submissionCount = ZipHelper.extractSubmissions(submissionDestPath, submissionDestPath)
    # Extract each submission zip file into its own directory
    submissionCount = ZipHelper.extractSubmissionZips(submissionDestPath)
    infoMessage = f"extractSubmissions - {submissionCount} submissions successfully extracted to {submissionDestPath}"
    Loghelper.logInfo(infoMessage)
    # delete all zip files
    for fiZip in [fi for fi in os.listdir(submissionDestPath) if fi.endswith("zip")]:
        fiPath = os.path.join(submissionDestPath, fiZip)
        os.remove(fiPath)
        infoMessage = f"extractSubmissions - {fiPath} deleted"
        Loghelper.logInfo(infoMessage)
    return submissionCount

'''
Gets all submissions from the database
'''
def getSubmissions() -> dict:
    submissionDic = DBHelper.getSubmissions(dbPath)
    print(submissionDic)

'''
Stores all submissions in the database
'''
def storeSubmissions():
    # delete all previous submissions
    DBHelper.clearAllSubmission(dbPath)
    submissionCounter = 0
    # get all submissions from the file system - key = exercise
    dicSubmissions = getSubmissions()
    for exercise in dicSubmissions:
        for studentId in dicSubmissions[exercise]:
            timestamp = datetime.datetime.now()
            try:
                DBHelper.storeSubmission(dbPath, timestamp, gradeSemester, gradeModule, exercise, studentId, False)
                submissionCounter += 1
            except Exception as ex:
                result = DBHelper.getStudentById(studentId)
                student = result[0] if len(result > 0) else ""
                infoMessage = f"Submission für Semester={gradeSemester} Modul={gradeModule} Exercise={exercise} Student={student} konnte nicht in der Datenbank gespeichert werden. ({ex})"
                Loghelper.logError(infoMessage)
    infoMessage = f"{submissionCounter} Abgaben wurden in der Datenbank gespeichert."
    Loghelper.logInfo(infoMessage)
    print(f"*** {infoMessage} ***")

'''
Output all submissions for a student by name 
'''
def showSubmissionsByStudent():
    studentName = input("Name des Studenten?")
    # Replace blank with _ if necessary
    studentName = studentName.replace(" ", "_")
    submissions = DBHelper.getSubmissionByStudent(dbPath, studentName)
    if len(submissions) == 0:
        print(f"Für Student {studentName} gibt es keine Abgaben")
    else:
        print(f"Abgaben von {studentName}")
        for submission in submissions:
            print(f">> {submission}")

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
Outputs all grade runs from the database
'''
def showGradingRuns():
    # returns tuples
    gradeRuns = DBHelper.getGradeRuns(dbPath)
    print("*" * 80)
    for gradeRun in gradeRuns:
        print(f"Id:{gradeRun[0]} Timestamp:{gradeRun[1]} Semester:{gradeRun[2]} Submission-Count:{gradeRun[3]}"
              f" OK-Count:{gradeRun[4]} ErrorCount:{gradeRun[5]}")
    print("*" * 80)
    print()


'''
Start a grading run
'''
def startGradingRun():
    # Initiate grading plan
    xmlHelper = XmlHelper(gradingPlanPath)
    # XSD validation - but no consequences yet
    xsdPath = os.path.join(os.path.dirname(__file__), "gradingplan.xsd")
    if os.path.exists(xsdPath):
        result = xmlHelper.validateXml(gradingPlanPath, xsdPath)
        infoMessage = f"XSD-Validierung: {result}"
        Loghelper.logInfo(infoMessage)

    # List for all grading actions for the grading Action report
    gradeActionList = []
    # List for all grading results for the grading Result report
    gradeResultList = []
    # Check if submissions had been already extracted
    if not os.path.exists(submissionDestPath):
        infoMessage = "Bitte zuerst alle Abgaben extrahieren!"
        print(infoMessage)
        return
    # get all Submissions from the file system as submission objects
    submissions = getSubmissions()
    # for clocking the grading run duration
    startTime = datetime.datetime.now()
    print(f"*** Starte Bewertung der Abgaben in {submissionPath} ***")
    # go through all submissions
    for submission in submissions:
        # get all the details from the submission object
        taskName = submission.exercise
        taskLevel = submission.level
        studentName = submission.student
        filePath = submission.filePath

        # go through all submitted files in the archive directory
        # get all file names from the gradinglan xml
        exerciseFiles = xmlHelper.getFileList(taskName, taskLevel)
        # get all file names from the submission
        submittedFiles = [fi for fi in os.listdir(filePath) if fi.endswith(".java")]
        # javaFiles = [fi for fi in os.listdir(archivePath) if fi.endswith(".java")]
        # check if files are missing in submitted files
        missingFiles = [fi for fi in exerciseFiles if fi not in submittedFiles]
        if len(missingFiles) > 0:
            infoMessage = f"!!! Missing files in Submission {submission.filePath}: {','.join(missingFiles)} !!!"
            Loghelper.logError(infoMessage)
            return -1
        for javaFile in submittedFiles:
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

    htmlPath = xmlHelper.convertGradingReport2Html(gradeReportPath, gradeSemester, gradeModule, gradeExercise)
    os.startfile(htmlPath)
    print(f"{len(submissions)} Submissions bearbeitet - OK: {okCount} Error: {errorCount}")


# =============================================================================
# Main Menue
# =============================================================================

'''
reads all the submissions from the file system
'''
def readSubmissions():
    submissionCount = extractMoodleSubmissions()
    infoMessage = f"{submissionCount} submissions eingelesen"
    Loghelper.logInfo(infoMessage)

'''
processes the submissions and store them in the database
'''
def processSubmissions():
    if submissionDic == None:
        print("*** Bitte zuerst alle Abgaben einlesen (Menüpunkt A) ***")
        return

    # Stores all submissions in the database
    storeSubmissions()

    # Store the complete student roster in the database
    RosterHelper.saveRosterInDb(dbPath, gradeSemester, gradeModule, studentRosterPath)

'''
Main starting point
'''
def start():
    initVariables()
    infoMessage = f"Starting {appName} (Version {appVersion}) - executing {gradingPlanPath}"
    Loghelper.logInfo(infoMessage)

    # for coloured output
    colorama.init()

    showBanner()

    # Create database
    if not os.path.exists(dbPath):
        DBHelper.initDb(dbPath)

    # process student roster file if exists
    if os.path.exists(studentRosterPath):
        RosterHelper.saveRosterInDb(dbPath, gradeSemester, gradeModule,  studentRosterPath)

    exitFlag = False
    while not exitFlag:
        choice = showMenu().upper()
        if choice == "Q":
            exitFlag = True
        elif choice == "A":                 # Read all submissions from the submission zip file
            readSubmissions()
        elif choice == "B":                 # Process all submissions from the submission directory
            processSubmissions()
        elif choice == "C":                 # Start grading all submissions
            startGradingRun()
        elif choice == "D":                 # Show all grading runs
            showGradingRuns()
        elif choice == "E":                 # Show gradings of a single student
            showGradingsByStudent()
        else:
            print(f"!!! {choice} ist eine relativ unbekannte Auswahl !!!")

# Starting point
if __name__ == "__main__":
    start()
