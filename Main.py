# =============================================================================
# Automatisiertes Bewerten von Java-Programmieraufgaben
# creation date: 03/01/22
# last update: 04/27/22
# Version 0.8
# =============================================================================
from datetime import datetime
import os
import re
import shutil
import tempfile
import configparser
import subprocess
import colorama
from colorama import Fore, Back, Style
import zipfile

import CheckstyleHelper
import JUnitHelper
import JavaFileHelper
import ZipHelper
import Loghelper

from GradeAction import GradeAction
from GradeResult import GradeResult
from FeedbackItem import FeedbackItem
from SubmissionName import SubmissionName
from SubmissionValidation import SubmissionValidation
import RosterHelper
import JavaHelper
import DBHelper
from XmlHelper import XmlHelper

from Submission import Submission
import csv

# =============================================================================
# Some global variables
# =============================================================================
appVersion = "0.80"
appName = "SimpelGrader"
# this path contains the path of the directory with the submitted zip file
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
    global submissionPath, gradingPlanPath, studentRosterPath, submissionDestPath
    global gradeModule, gradeSemester, gradingOperator, deleteSubmissionTree
    global dbPath
    config = configparser.ConfigParser()
    config.read("Simpelgrader.ini")
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
    # Delete the today log file if it already exists
    deleteLogfile = config["start"]["deleteLogfile"]
    if deleteLogfile.upper().startswith("Y") and os.path.exists(Loghelper.logPath):
            os.remove(Loghelper.logPath)
    # Delete the directory if it already exists
    deleteSubmissionTree = config["start"]["deleteSubmissionTree"]
    if deleteSubmissionTree.upper().startswith("Y") and os.path.exists(submissionDestPath):
        shutil.rmtree(submissionDestPath)
        infoMessage = f"initVariables: deleted directory {submissionDestPath} with its content"
        Loghelper.logInfo(infoMessage)
    if not os.path.exists(submissionDestPath):
        # create directory with all the subdirectories
        os.makedirs(submissionDestPath)
        infoMessage = f"initVariables: created directory {submissionDestPath}"
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
    menuList.append("Precheck der Ini-Einstellungen (optional")
    menuList.append("Alle Abgaben aus Zip-Archiv einlesen")
    menuList.append("Abgaben validieren (optional)")
    menuList.append(Fore.LIGHTYELLOW_EX + "Bewertungsdurchlauf starten" + Style.RESET_ALL)
    menuList.append("Bewertungsdurchläufe anzeigen")
    menuList.append("Studentenroster anzeigen")
    menuList.append("Alle Abgaben anzeigen")
    menuList.append("Logdatei anzeigen")
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
Menue A - checks if the ini settings are valid
'''
def MenueA_preCheck() -> None:
    dicCheck = {}
    errorFlag = False
    if not os.path.exists(gradingPlanPath):
        print(f"!!! {gradingPlanPath} existiert nicht")
        errorFlag = True
    dicCheck["gradingPlan"] = (gradingPlanPath, errorFlag)
    # validate grading xml file
    if os.path.exists(gradingPlanPath):
        xmlHelper = XmlHelper(gradingPlanPath)
        result = xmlHelper.validateXml()
        dicCheck["gradingPlanValidation"] = ("Keine Ausgabe", result)
    errorFlag = False
    if not os.path.exists(submissionPath):
        print(f"!!! {submissionPath} existiert nicht")
        errorFlag = True
    dicCheck["submissionPath"] = (submissionPath, errorFlag)
    errorFlag = False
    if not os.path.exists(studentRosterPath):
        print(f"!!! {studentRosterPath} existiert nicht")
        errorFlag = True
    dicCheck["studentRoster"] = (studentRosterPath, errorFlag)
    errorFlag = False
    if not os.path.exists(dbPath):
        print(f"!!! {dbPath} existiert nicht")
        errorFlag = True
    dicCheck["dbPath"] = (dbPath, errorFlag)

    print("*" * 80)
    for checkName,checkValue in dicCheck.items():
        if checkValue[1]:
            print(f"{checkName}={Fore.LIGHTRED_EX}{checkValue[0]}{Style.RESET_ALL}")
        else:
            print(f"{checkName}={Fore.LIGHTGREEN_EX}{checkValue[0]}{Style.RESET_ALL}")

    print("*" * 80)
    okChecks = len([c for c in dicCheck if dicCheck[c][1]==False])
    print(f"*** {okChecks} von {len(dicCheck)} Settings sind OK ***")
    print("*" * 80)

'''
Menue B - extracts all submission files from a single zip file in the submissionPath directory
'''
def MenueB_extractSubmissions() -> None:
    global submissionDic
    # validate the roster file first
    if not RosterHelper.validateRoster(studentRosterPath):
        # roster file is not valid exit
        return

    print(Fore.LIGHTMAGENTA_EX + "*** Alle Abgaben werden extrahiert - bitte etwas Geduld ***" + Style.RESET_ALL)

    # the the single zip file that contains all the submissions
    zipFiles = [fi for fi in os.listdir(submissionPath) if fi.endswith("zip")]
    # only one zip file allowed
    if len(zipFiles) != 1:
        infoMessage = f"extractSubmissions: exactly one zip file expected in {submissionPath}"
        Loghelper.logError(infoMessage)
        return False
    # get the full path of the zip file
    zipPath = os.path.join(submissionPath, zipFiles[0])

    if not os.path.exists(submissionDestPath):
        os.mkdir(submissionDestPath)
        infoMessage = f"extractSubmissions: directory {submissionDestPath} created"
        Loghelper.logInfo(infoMessage)

    # Copy zip file to temp directory
    shutil.copy(zipPath, submissionDestPath)

    # change zipPath to new location
    zipPath = os.path.join(submissionDestPath, os.path.basename(zipPath))

    # Store the complete student roster in the database
    RosterHelper.saveRosterInDb(dbPath, gradeSemester, gradeModule, studentRosterPath)

    # extract alle the submissions from the downloaded zip file
    # dbPath for getStudentId query - maybe better solution?
    submissionDic = ZipHelper.extractSubmissions(dbPath, zipPath, submissionDestPath)

    # Update semester and module for each submission
    for exercise in submissionDic:
        for studentName in submissionDic[exercise]:
            for submission in submissionDic[exercise][studentName]:
                submission.semester = gradeSemester
                submission.module = gradeModule

    # flatten the dic to get the total count of all submissions
    submissionCount = len([item for sublist in [submissionDic[k] for k in submissionDic] for item in sublist])
    infoMessage = f"extractSubmissions: {submissionCount} submissions for {len(submissionDic)} exercise extracted from the Moodle zip file"
    Loghelper.logInfo(infoMessage)

    # delete all previous submissions
    DBHelper.clearAllSubmission(dbPath)

    # go through all the submissions from the dictionary for storing them into the database
    submissionProcessedCount = 0
    for exercise in submissionDic:
        for studentName in submissionDic[exercise]:
            # take only the first submission at the moment
            submission = submissionDic[exercise][studentName][0]
            studentId = submission.studentId
            files = submission.files
            dirPath = submission.path
            # complete is always false at this time because
            # the completenes of the files have not been checked yet
            complete = submission.complete
            timestamp = datetime.now()
            DBHelper.storeSubmission(dbPath, timestamp, gradeSemester, gradeModule, exercise, studentId, files, dirPath, complete)
            submissionProcessedCount += 1

    infoMessage = f"{submissionProcessedCount} submissions stored in the database."
    Loghelper.logInfo(infoMessage)

    # update the roster with the exercises
    RosterHelper.updateStudentRoster(dbPath, submissionDic)

    print(Fore.LIGHTYELLOW_EX + "*" * 80)
    print(f"*** {submissionProcessedCount} Abgaben wurden verarbeitet ***")
    print("*" * 80 + Style.RESET_ALL)

'''
Menue C - validates all submissions in the database
'''
def MenueC_validateSubmissions() -> None:
    global submissionDic
    # Any submissions in the dic yet?
    if submissionDic == None:
        # Try again, submissions already extracted?
        submissionDic = ZipHelper.buildSubmissionDic(dbPath, submissionDestPath)
        # Any submissions?
        if len(submissionDic) == 0:
            print(Fore.LIGHTRED_EX + "*** Bitte zuerst alle Abgaben einlesen (Menüpunkt B) ***" + Style.RESET_ALL)
            return
    validationList = []

    print(Fore.LIGHTMAGENTA_EX + "*** Alle Abgaben werden validiert - bitte etwas Geduld ***" + Style.RESET_ALL)

    # go through all the submitted directories with their java files
    xmlHelper = XmlHelper(gradingPlanPath)
    # go through each exercise
    for exercise in submissionDic:
        # check if all student from the roster have valid submissions
        exerciseSubmissions = submissionDic[exercise]
        # go through each submissions for this exercise by student name
        for studentName in exerciseSubmissions:
            infoMessage = f"validateSubmissions: validating submission for student {studentName}"
            Loghelper.logInfo(infoMessage)
            # go through the (single) submissions of that particular student
            for submission in submissionDic[exercise][studentName]:
                exercise = submission.exercise
                files = submission.files.split(",")
                # get the files from the grading plan
                exerciseFiles = xmlHelper.getFileList(exercise)
                # check if all submissions are complete
                missingFiles = [fi for fi in exerciseFiles if fi not in files]
                if len(missingFiles) > 0:
                    infoMessage = f"Missing files in submission {submission.id}: {','.join(missingFiles)}"
                    Loghelper.logError(f"validateSubmissions: {infoMessage}")
                    validation = SubmissionValidation(exercise, "Error", infoMessage)
                    # update submission info
                    submission.complete = False
                else:
                    infoMessage = f"All files complete"
                    validation = SubmissionValidation(exercise, "OK", infoMessage)
                    # update submission info
                    submission.complete = True

                # update submission in the database
                DBHelper.updateSubmission(dbPath, submission)

                # update validation details
                validation.submissionId = submission.id
                validation.studentId = submission.studentId
                validationList.append(validation)

    # create a xml report
    xmlPath = xmlHelper.generateSubmissionValidationReport(validationList)

    # create a html report
    htmlPath = xmlHelper.convertSubmissionValidationReport2Html(xmlPath)
    # show html file in browser
    os.startfile(htmlPath)

    print("*" * 80)
    print(f"*** Alle Abgaben wurden validiert ***")
    print("*" * 80)

'''
Menue D - starts a grading run for the submissions in the database
'''
def MenueD_startGradingRun() -> None:
    # Any submissions in the dic yet?
    if submissionDic == None:
        print(Fore.LIGHTRED_EX + "*** Bitte zuerst alle Abgaben einlesen (Menüpunkt B) ***" + Style.RESET_ALL)
        return
    # Initiate grading plan
    xmlHelper = XmlHelper(gradingPlanPath)
    # XSD validation of the grading plan xml - but no consequences yet
    result = xmlHelper.validateXml()
    infoMessage = f"startGradingRun: XSD-Validierung: {result}"
    Loghelper.logInfo(infoMessage)

    # List for all grading actions for the grading Action report
    gradeActionList = []
    # List for all grading results for the grading Result report
    gradeResultList = []
    # List for the feedback items
    feedbackItemList = []
    submisssionsGraded = 0

    # for clocking the grading run duration
    startTime = datetime.now()
    print(Fore.LIGHTGREEN_EX +  f"*** Starte GradingRun für die Aufgaben {','.join(submissionDic.keys())}  ***" + Style.RESET_ALL)
    # go through all submissions
    for exercise in submissionDic:
        # get all the details from the submission object
        for studentName in submissionDic[exercise]:
            for submission in submissionDic[exercise][studentName]:
                infoMessage = f"startGradingRun: grading submission {submission.id}/{submission.exercise} for student {studentName}"
                Loghelper.logInfo(infoMessage)
                print(f"*** Starte Bewertung für Abgabe {submission.id}/{submission.exercise} und Student {studentName} ({submission.studentId}) ***")
                # go through all submitted files in the archive directory
                # get all file names from the gradingplan xml
                # check if exercise exists in the gradingplan
                if not xmlHelper.exerciseExists(exercise):
                    infoMessage = f"startGradingRun: no grading plan for exercise {exercise}"
                    Loghelper.logError(infoMessage)
                    print(Fore.LIGHTYELLOW_EX +  f"*** Kein Eintrag für Aufgabe {exercise} - Aufgabe wird nicht bewertet ***" + Style.RESET_ALL)
                    continue
                # get the expected files from the grading plan
                exerciseFiles = xmlHelper.getFileList(exercise)
                # get all file names from the submission
                files = submission.files.split(",")
                filesPath = submission.path
                # check if files are missing in submitted files
                missingFiles = [fi for fi in exerciseFiles if fi not in files]
                if len(missingFiles) > 0:
                    infoMessage = f"startGradingRun: missing files in submission {submission.id}: {','.join(missingFiles)}"
                    Loghelper.logError(infoMessage)
                for javaFile in files:
                    # Get all actions for the task from the xml file
                    actionList = xmlHelper.getActionList(exercise)
                    # Go through all the actions
                    for action in actionList:
                        # skip not active actions
                        if not eval(action.active):
                            infoMessage = f"startGradingRun: leaving out action {action.command} for {javaFile}"
                            Loghelper.logInfo(infoMessage)
                            continue
                        # Execute the action
                        infoMessage = f"startGradingRun: executing action {action.command} for {javaFile}/StudentId: {submission.studentId}"
                        Loghelper.logInfo(infoMessage)
                        # the action depends on the action type
                        if action.type == "java-compile":
                            # a new item for the action report
                            gradeAction = GradeAction(action.type, "compile")
                            gradeAction.submission = submission
                            gradeAction.file = javaFile
                            gradeActionList.append(gradeAction)
                            # a new item for the grade result report
                            gradeResult = GradeResult(action.type)
                            gradeResult.description = f"Compiling {javaFile}"
                            javaFilePath = os.path.join(filesPath, javaFile)
                            # JUnit test file names follow the pattern <name>Test.java
                            if not javaFile.split(".")[0].lower().endswith("test"):
                                # compile the java file - the result is either 1 or 0
                                compileResult = JavaHelper.compileJava(javaFilePath)
                            else:
                                compileResult = JUnitHelper.compileJavaTest(javaFilePath)
                            gradePoints = 1 if compileResult[0] == 0 else 0
                            gradeResult.points = gradePoints
                            gradeResult.errorMessage = compileResult[1]
                            # TODO: what makes a  success?
                            actionSuccess = gradePoints > 0
                            gradeResult.success = actionSuccess
                            gradeResult.submission = submission
                            gradeResultList.append(gradeResult)
                            # Create a feedback object for the action
                            feedbackItem = FeedbackItem(submission)
                            feedbackItem.report = compileResult[1]
                            feedbackItemList.append(feedbackItem)
                        else:
                            infoMessage = f"startGradingRun: {action.type} is an unknown action type"
                            Loghelper.logInfo(infoMessage)

                    # Get all the tests for the exercise
                    testList = xmlHelper.getTestList(exercise)
                    for test in testList:
                        # is the test active? it has to be True and not true in the xml
                        if not eval(test.active):
                            infoMessage = f"startGradingRun: leaving out Test {test.id} for {javaFile}"
                            Loghelper.logInfo(infoMessage)
                            continue

                        infoMessage = f"startGradingRun: executing test {test.id} for file {javaFile}"
                        Loghelper.logInfo(infoMessage)

                        points = 0
                        # a new GradeAction object just for the report
                        gradeAction = GradeAction(test.type, "test")
                        gradeAction.submission = submission
                        gradeAction.file = javaFile
                        gradeActionList.append(gradeAction)

                        gradeResult = GradeResult(f"{test.type}-Test")
                        gradeResult.submission = submission
                        # what test to run?
                        if test.type.lower() == "checkstyle":
                            # TODO: get the Checkstyle messages?
                            points += CheckstyleHelper.runCheckstyle(javaFile)
                        elif test.type.lower() == "junit":
                            points += JUnitHelper.runJUnitTest(javaFile)
                        elif test.type.lower() == "textcompare":
                            pass
                        elif test.type.lower() == "testdriver":
                            pass
                        else:
                            infoMessage = f"startGradingRun: {test.type} is an unknown test type"
                            Loghelper.logInfo(infoMessage)
                        # TODO: Natürlich nur provisorisch
                        gradeResult.points = points
                        gradeResult.success = True if points > 0 else False
                        gradeResultList.append(gradeResult)

                        # Create a feedback object for the action
                        feedbackItem = FeedbackItem(submission)
                        feedbackItem.report = compileResult[1]
                        feedbackItemList.append(feedbackItem)

                # count the graded submissions
                submisssionsGraded += 1

                # prepare to store the current submission in the database

                # get the sum of all points for the current submission
                totalGradePoints = sum([g.points for g in gradeResultList if g.submission.id == submission.id])
                # get the number of errors for the current submission
                gradeErrors = sum([1 for g in gradeResultList if g.success == False])
                # get the next id from the gradeRun table
                gradeRunId = DBHelper.getNextGradeRunId(dbPath)
                # store the current submission in the database
                DBHelper.storeSubmissionResult(dbPath, gradeRunId, submission.id, exercise, gradeSemester,
                                               gradeModule, totalGradePoints, gradeErrors)


    # Prepare to store current graderun in the database
    timestamp = datetime.now().strftime("%d.%m.%y %H:%M")
    # get the total of all oks
    okCount = len([gr for gr in gradeResultList if gr.success])
    # get the total of all errors
    errorCount = len([gr for gr in gradeResultList if not gr.success])
    # store the graderun in the database
    gradeRunId = DBHelper.storeGradeRun(dbPath, timestamp, gradeSemester, gradeModule, gradingOperator, submisssionsGraded, okCount, errorCount)
    infoMessage = f"startGradingRun: stored gradeRun id={gradeRunId}"
    Loghelper.logInfo(infoMessage)

    # write the xml report for the grading actions
    actionReportPath = xmlHelper.generateGradingActionReport(gradeActionList)
    # display report file
    subprocess.call(["notepad.exe", actionReportPath])

    # write the xml report for the grading results
    gradeReportPath = xmlHelper.generateGradingResultReport(gradeResultList)
    # display report file
    subprocess.call(["notepad.exe", gradeReportPath])

    # convert the grading results reports to html
    htmlPath = xmlHelper.convertGradingResultReport2Html(gradeReportPath, gradeSemester, gradeModule, exercise)
    os.startfile(htmlPath)
    print(f"{submisssionsGraded} Submissions bearbeitet - OK: {okCount} Error: {errorCount}")

    # TODO: create a feedback report

'''
Menue E - outputs all grading runs in the database
'''
def MenueE_showGradingRuns() -> None:
    # returns tuples
    gradeRuns = DBHelper.getAllGradeRuns(dbPath)
    print("*" * 80)
    for gradeRun in gradeRuns:
        print(Fore.LIGHTGREEN_EX +  f'Id:{gradeRun["Id"]} Timestamp:{gradeRun["Timestamp"]} Semester:{gradeRun["Semester"]} Submission-Count:{gradeRun["SubmissionCount"]} '
              f'OK-Count:{gradeRun["OKCount"]} ErrorCount:{gradeRun["ErrorCount"]}' + Style.RESET_ALL)
    print("*" * 80)
    print()

'''
Menue F - outputs the current student roster from the database 
'''
def MenueF_showStudentRoster() -> None:
    rosters = DBHelper.getRoster(dbPath)
    for roster in rosters:
        print(Fore.LIGHTCYAN_EX +  f"{roster}" + Style.RESET_ALL)

'''
Menue G - outputs the submissions of all students from the database 
'''
def MenueG_showStudentSubmissions() -> None:
    submissionDic = DBHelper.getSubmissions(dbPath)
    # transform to a dict with student as key
    studentDic = {}
    if submissionDic == None:
        print(Fore.LIGHTRED_EX +  f"*** Keine Submissions in der Datenbank ***" + Style.RESET_ALL)
    else:
        for exercise in submissionDic:
            for student in submissionDic[exercise]:
                if student == None:
                    continue
                studentName = f"{student.firstName}_{student.lastName}"
                if studentDic.get(studentName) == None:
                    studentDic[studentName] = []
                for submission in submissionDic[exercise][student]:
                    studentDic[studentName].append(submission)
        for studentName in studentDic:
            print(f"*** Abgaben für Student {studentName}")
            for submission in studentDic[studentName]:
                if submission.complete:
                    print(Fore.LIGHTGREEN_EX + f">>> {submission.exercise}" + Style.RESET_ALL)
                else:
                    print(Fore.LIGHTYELLOW_EX + f">>> {submission.exercise}" + Style.RESET_ALL)


'''
Menue H - show current log file
'''
def MenueH_showLogfile() -> None:
    if os.path.exists(Loghelper.logPath):
        subprocess.Popen(["notepad", Loghelper.logPath])
    else:
        print(f"!!! {Loghelper.logPath} existiert nicht !!!")

# =============================================================================
# Starting point
# =============================================================================

'''
Main function for the application
'''
def start() -> None:
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
        elif choice == "A":                 # checks ini settings
            MenueA_preCheck()
        elif choice == "B":                 # Process all submissions from the submission zip file
            MenueB_extractSubmissions()
        elif choice == "C":                 # Validates submissions in the database for missing submissions and files
            MenueC_validateSubmissions()
        elif choice == "D":                 # Start grading all submissions
            MenueD_startGradingRun()
        elif choice == "E":                 # Show all grading runs
            MenueE_showGradingRuns()
        elif choice == "F":                 # Shows the current student roster
            MenueF_showStudentRoster()
        elif choice == "G":                 # Show gradings of a single student
            MenueG_showStudentSubmissions()
        elif choice == "H":
            MenueH_showLogfile()
        else:
            print(f"!!! {choice} ist eine relativ unbekannte Auswahl !!!")

    # copy the database file for a backup
    config = configparser.ConfigParser()
    config.read("Simpelgrader.ini")
    databaseBackup = config["start"]["databaseBackup"]
    if databaseBackup.upper().startswith("Y") and os.path.exists(dbPath):
        n = 0
        abbruch = False
        while not abbruch:
            n += 1
            dbName = dbPath.split(".")[0]
            dbCopyPath = f"{dbName}_{n:03d}.db"
            abbruch = not os.path.exists(dbCopyPath) or n == 999
        shutil.copy(dbPath, dbCopyPath)
        infoMessage = f"start: copied {dbPath} to {dbCopyPath}"
        Loghelper.logInfo(infoMessage)
        print(Fore.LIGHTYELLOW_EX +  f"*** copied {dbPath} to {dbCopyPath} ***" + Style.RESET_ALL)

# The "real" starting point for the case that someone thinks this is a module;)
if __name__ == "__main__":
    start()
