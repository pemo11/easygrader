# =============================================================================
# Automatic grading of Java programming assignments
# creation date: 03/01/22
# last update: 07/05/22
# Version 0.8
# =============================================================================
import random
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

import CheckstyleTestHelper
import CompareTestHelper
import JUnitTestHelper
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
simpelgraderDir = ""
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

'''
Initialize the application after the start
'''
def initApp():
    global simpelgraderDir
    initVariables()
    config = configparser.ConfigParser()
    config.read("Simpelgrader.ini")
    # Delete the today log file if it already exists
    deleteLogfile = config["start"]["deleteLogfile"]
    if deleteLogfile.upper().startswith("Y") and os.path.exists(Loghelper.logPath):
            os.remove(Loghelper.logPath)
    # Delete the directory if it already exists
    deleteSubmissionTree = config["start"]["deleteSubmissionTree"]
    if deleteSubmissionTree.upper().startswith("Y") and os.path.exists(submissionDestPath):
        shutil.rmtree(submissionDestPath)
        infoMessage = f"initializeApp: deleted directory {submissionDestPath} with its content"
        Loghelper.logInfo(infoMessage)
    if not os.path.exists(submissionDestPath):
        # create directory with all the subdirectories
        os.makedirs(submissionDestPath)
        infoMessage = f"initializeApp: created directory {submissionDestPath}"
        Loghelper.logInfo(infoMessage)
    simpelgraderDir = os.path.join(os.path.expanduser("~"), "documents/simpelgrader")
    # create directory for report files
    if not os.path.exists(simpelgraderDir):
        os.mkdir(simpelgraderDir)
        infoMessage = f"initializeApp: created directory {simpelgraderDir}"
        Loghelper.logInfo(infoMessage)

# =============================================================================
# Helper functions
# =============================================================================

'''
get a quote from the quotes.txt file
'''
def getQuote() -> str:
    quote = ""
    if os.path.exists("quotes.txt"):
        with open ("quotes.txt", mode="r",encoding="utf8") as fh:
            quotes = [li.strip() for li in fh.readlines()]
        z = random.randint(0, len(quotes)-1)
        quote = quotes[z]
    return quote


'''
Shows the Welcome Banner
'''
def showBanner():
    print(Fore.LIGHTGREEN_EX + "*" * 80)
    print(f"{'*' * 24}{f' Welcome to {appName} {appVersion} '}{'*' * 25}")
    quote = getQuote()
    if quote != "":
        starCount = (80 - len(quote)) // 2
        print(f"{'*' * (starCount-1)} ({quote}) {'*' * (starCount-2)}")
    print("*" * 80 + Style.RESET_ALL)

'''
Shows application main menue
'''
def showMenu():
    menuList = []
    menuList.append("Precheck der Ini-Einstellungen (optional)")
    menuList.append(Fore.LIGHTYELLOW_EX + "Alle Abgaben aus Zip-Archiv einlesen" + Style.RESET_ALL)
    menuList.append("Abgaben validieren (optional)")
    menuList.append(Fore.LIGHTYELLOW_EX + "Bewertungsdurchlauf starten" + Style.RESET_ALL)
    menuList.append("Bewertungsdurchläufe anzeigen")
    menuList.append("Studentenroster anzeigen")
    menuList.append("Alle Abgaben anzeigen")
    menuList.append("Logdatei anzeigen")
    menuList.append("Simpelgrader.ini erstellen (optional)")
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
    config = configparser.ConfigParser()
    config.read("Simpelgrader.ini")
    print("*" * 80)
    # check if the gradingfile xml file path exists
    if not os.path.exists(gradingPlanPath):
        print(f"!!! {gradingPlanPath} existiert nicht")
        errorFlag = True
    dicCheck["gradingPlanPath"] = (gradingPlanPath, errorFlag)
    # validate grading xml file
    if os.path.exists(gradingPlanPath):
        xmlHelper = XmlHelper(gradingPlanPath)
        result = xmlHelper.validateXml()
        dicCheck["gradingPlanValidation"] = ("Keine Ausgabe", result)
    errorFlag = False
    # check if the submission dir path exists
    if not os.path.exists(submissionPath):
        print(f"!!! {submissionPath} existiert nicht")
        errorFlag = True
    dicCheck["submissionPath"] = (submissionPath, errorFlag)
    errorFlag = False
    # check if the student roster file exists
    if not os.path.exists(studentRosterPath) or not os.path.isfile(studentRosterPath):
        print(f"!!! {studentRosterPath} existiert nicht")
        errorFlag = True
    dicCheck["studentRosterPath"] = (studentRosterPath, errorFlag)
    # check if the db file exists
    errorFlag = False
    if not os.path.exists(dbPath) or not os.path.isfile(dbPath):
        print(f"!!! {dbPath} existiert nicht")
        errorFlag = True
    dicCheck["dbPath"] = (dbPath, errorFlag)
    # check if the javac file exists
    errorFlag = False
    javaCPath = config["path"]["javaCompilerPath"]
    # if Windows, add exe extension for the test
    if os.name == "nt":
        javaCPath += ".exe"
    if not os.path.exists(javaCPath) or not os.path.isfile(javaCPath):
        print(f"!!! {javaCPath} existiert nicht")
        errorFlag = True
    dicCheck["javaCPath"] = (javaCPath, errorFlag)
    # check if the java file exists
    errorFlag = False
    javaPath = config["path"]["javaLauncherPath"]
    # if Windows, add exe extension for the test
    if os.name == "nt":
        javaPath += ".exe"
    if not os.path.exists(javaPath) or not os.path.isfile(javaPath):
        print(f"!!! {javaPath} existiert nicht")
        errorFlag = True
    dicCheck["javaPath"] = (javaPath, errorFlag)
    # check if the checkstyle jar file exists
    errorFlag = False
    checkstyleJarPath = config["path"]["checkstylePath"]
    if not os.path.exists(checkstyleJarPath) or not os.path.isfile(checkstyleJarPath):
        print(f"!!! {checkstyleJarPath} existiert nicht")
        errorFlag = True
    dicCheck["checkstyleJarPath"] = (checkstyleJarPath, errorFlag)
    # check if the checkstyle rule file exists
    errorFlag = False
    checkstyleRulePath = config["path"]["checkstyleRulePath"]
    if not os.path.exists(checkstyleRulePath) or not os.path.isfile(checkstyleRulePath):
        print(f"!!! {checkstyleRulePath} existiert nicht")
        errorFlag = True
    dicCheck["checkstyleRulePath"] = (checkstyleRulePath, errorFlag)
    # check if the JUnit directory exists
    errorFlag = False
    jUnitPath = config["path"]["jUnitPath"]
    if not os.path.exists(jUnitPath) or not os.path.isdir(jUnitPath):
        print(f"!!! {jUnitPath} existiert nicht")
        errorFlag = True
    dicCheck["jUnitPath"] = (jUnitPath, errorFlag)

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
        print(Fore.LIGHTRED_EX + f"*** Datei {studentRosterPath} nicht gefunden - bitte den Pfad ändern! ***" + Style.RESET_ALL)
        return

    print(Fore.LIGHTMAGENTA_EX + "*** Alle Abgaben werden extrahiert - bitte etwas Geduld ***" + Style.RESET_ALL)

    # the the single zip file that contains all the submissions
    zipFiles = [fi for fi in os.listdir(submissionPath) if fi.endswith("zip")]
    # only one zip file allowed
    if len(zipFiles) != 1:
        infoMessage = f"extractSubmissions: exactly one zip file expected in {submissionPath}"
        Loghelper.logWarning(infoMessage)
        print(Fore.LIGHTRED_EX + f"*** Im Verzeichnis {submissionPath} darf sich nur eine Zip-Datei befinden! ***" + Style.RESET_ALL)
        return

    # get the full path of the zip file
    zipPath = os.path.join(submissionPath, zipFiles[0])

    # create the submission dest directory if it does not exists
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

    # any submission extracted?
    if submissionCount == 0:
        print(Fore.LIGHTRED_EX + f"*** Im Verzeichnis {submissionPath} wurden keine Abgaben gefunden! ***" + Style.RESET_ALL)
        return

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

    # any submission processed?
    if submissionProcessedCount == 0:
        print(Fore.LIGHTRED_EX + f"*** Es wurden keine Abgaben verarbeitet! ***" + Style.RESET_ALL)
        return

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
                    Loghelper.logWarning(f"validateSubmissions: {infoMessage}")
                    validation = SubmissionValidation(exercise, "Error", infoMessage)
                    print(Fore.LIGHTYELLOW_EX + "*** Fehlende Dateien: {','.join(missingFiles)} ***" + Style.RESET_ALL)
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
    if submissionDic == None or (submissionDic != None and len(submissionDic) == 0):
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
                problemCount = 0
                infoMessage = f"startGradingRun: grading submission {submission.id}/{submission.exercise} for student {studentName}"
                Loghelper.logInfo(infoMessage)
                print(f"*** Starte Bewertung für Abgabe {submission.id}/{submission.exercise} und Student {studentName} ({submission.studentId}) ***")
                # go through all submitted files in the archive directory
                # get all file names from the gradingplan xml
                # check if exercise exists in the gradingplan
                if not xmlHelper.exerciseExists(exercise):
                    infoMessage = f"startGradingRun: no grading plan for exercise {exercise}"
                    Loghelper.logWarning(infoMessage)
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
                    Loghelper.logWarning(infoMessage)
                    print(Fore.LIGHTYELLOW_EX + "*** Fehlende Dateien: {','.join(missingFiles)} ***" + Style.RESET_ALL)
                    problemCount += 1
                # run the action for each java file
                for javaFile in files:
                    javaFilePath = os.path.join(filesPath, javaFile)
                    # get all actions for the task from the xml file
                    actionList = xmlHelper.getActionList(exercise)
                    # go through all the actions
                    for action in actionList:
                        # skip not active actions
                        if not eval(action.active):
                            infoMessage = f"startGradingRun: leaving out action {action.command} for {javaFile}"
                            Loghelper.logInfo(infoMessage)
                            continue
                        # execute the action
                        infoMessage = f"startGradingRun: executing action {action.command} for {javaFile} StudentId: {submission.studentId}"
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
                            # javaFilePath = os.path.join(filesPath, javaFile)
                            # JUnit test file names follow the pattern <name>Test.java
                            if not javaFile.split(".")[0].lower().endswith("test"):
                                # compile the java file - the result is either 1 or 0
                                compileResult = JavaHelper.compileJava(javaFilePath)
                            else:
                                compileResult = JUnitTestHelper.compileJavaTest(javaFilePath)
                            # now the jury verdict...
                            actionPoints = xmlHelper.getActionPoints(exercise, action.id)
                            gradePoints = actionPoints if compileResult[0] == 0 else 0
                            gradeResult.points = gradePoints
                            gradeResult.errorMessage = compileResult[1]
                            problemCount += 1 if compileResult[0] == 1 else 0
                            # TODO: what makes a  success?
                            actionSuccess = gradePoints > 0
                            gradeResult.success = actionSuccess
                            gradeResult.submission = submission
                            gradeResultList.append(gradeResult)
                            # Create a feedback object for the action
                            # TODO: better mechanismen for generating the id (if necessary at all)
                            feedbackItemid = len(feedbackItemList) + 1
                            feedbackItem = FeedbackItem(feedbackItemid, submission)
                            feedbackItem.message = compileResult[1]
                            # TODO: When high?
                            feedbackItem.severity = "normal"
                            feedbackItemList.append(feedbackItem)
                        else:
                            infoMessage = f"startGradingRun: {action.type} is an unknown action type"
                            Loghelper.logInfo(infoMessage)

                # variables must exist ?
                jUnitReportHtmlPath = ""
                checkstyleReportHtmlPath = ""
                textcomparePath = ""

                # run the test for each java file
                for javaFile in files:
                    # don't test the JUnit and the tester classes
                    javaFileName = javaFile.split(".")[0].lower()
                    if javaFileName.endswith("test") or javaFileName.endswith("tester"):
                        infoMessage = f"startGradingRun: skipped test for file {javaFile}"
                        Loghelper.logInfo(infoMessage)
                        continue

                    # build the file path
                    javaFilePath = os.path.join(submission.path, javaFile)

                    # get all the tests for the exercise
                    testList = xmlHelper.getTestList(exercise)
                    for test in testList:
                        # is the test active? it has to be True not true in the xml
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
                        gradeResult.description = f"Running {test.type}-Test"

                        # what test to run?
                        # a checkstyle test?
                        if test.type.lower() == "checkstyle":
                            # return value is a tuple (returncode, message)
                            checkstyleResult, checkstyleMessage = CheckstyleTestHelper.runCheckstyle(javaFilePath)
                            testPoints = xmlHelper.getTestPoints(exercise,test.id)
                            points += testPoints if checkstyleResult == 0 else 0
                            # don't forget the points
                            gradeResult.points = points
                            problemCount += 1 if checkstyleResult != 0 else 0
                            # TODO: better message
                            gradeResult.errorMessage = "OK" if checkstyleResult == 0 else "Error"
                            # store the checkstyle report as xml
                            checkstyleName = f"{studentName}_{exercise}_CheckstyleResult.xml"
                            checkstyleReportpath = os.path.join(simpelgraderDir, checkstyleName)
                            with open(checkstyleReportpath, mode="w", encoding="utf8") as fh:
                                checkstyleLines = checkstyleMessage.split("\n")
                                fh.writelines(checkstyleLines)
                            infoMessage = f"startGradingRun: saved checkstyle report {checkstyleName}"
                            Loghelper.logInfo(infoMessage)
                            # convert the xml to html
                            checkstyleReportHtmlPath = xmlHelper.convertCheckstyleReport2Html(checkstyleReportpath, studentName, exercise)

                        # a junit test?
                        elif test.type.lower() == "junit":
                            dirPath = os.path.dirname(javaFilePath)
                            testClassName = test.testClass
                            junitResult,junitXmlMessage = JUnitTestHelper.runJUnitTest(dirPath, testClassName)
                            if junitResult == 0:
                                # get the points for this exercise
                                testPoints = xmlHelper.getTestPoints(exercise,test.id)
                                points += testPoints
                            problemCount += 1 if junitResult != 0 else 0
                            # TODO: better message
                            gradeResult.result = True if junitResult == 0 else False
                            # don't forget the points
                            gradeResult.points = points
                            if junitXmlMessage != "":
                                gradeResult.errorMessage = f"JUnit-Result: {JUnitTestHelper.getJUnitResult(junitXmlMessage)}"
                                jUnitName = f"{studentName}_{exercise}_JUnitResult.xml"
                                jUnitReportpath = os.path.join(simpelgraderDir, jUnitName)
                                with open(jUnitReportpath, mode="w", encoding="utf8") as fh:
                                    jUnitLines = junitXmlMessage.split("\n")
                                    fh.writelines(jUnitLines)
                                infoMessage = f"startGradingRun: saved JUnit report {jUnitName}"
                                Loghelper.logInfo(infoMessage)
                                # convert the xml to html
                                jUnitReportHtmlPath = xmlHelper.convertJUnitReport2Html(jUnitReportpath, studentName, exercise)
                            else:
                                gradeResult.errorMessage = f"JUnit-Result: JUnit could not run"

                        # a textcompare test?
                        elif test.type.lower() == "textcompare":
                            classPath = javaFilePath.split(".")[0]
                            # return value is a tuple of three
                            textcompareResult, textcompareMessage, compareLines = CompareTestHelper.runTextCompare(classPath, exercise)
                            gradeResult.errorMessage = textcompareMessage
                            # get the points for this exercise
                            testPoints = xmlHelper.getTestPoints(exercise,test.id)
                            gradeResult.points = testPoints if textcompareResult == 0 else 0
                            # TODO: Only provisional of course - better definition for successs needed
                            gradeResult.result = True if textcompareResult == 0 else False
                            gradeResult.success = True if points > 0 else False
                            if len(compareLines) > 0:
                                textcompareName = f"{studentName}_{exercise}_TextCompareResult.txt"
                                textcomparePath = os.path.join(simpelgraderDir, textcompareName)
                                with open(textcomparePath, mode="w", encoding="utf8") as fh:
                                    fh.write(f"Text-Compare-Result für {studentName}/{exercise}\n")
                                    fh.write(textcompareMessage + "\n")
                                    fh.writelines(compareLines)
                                infoMessage = f"startGradingRun: saved Text-Compare report {textcompareName}"
                                Loghelper.logInfo(infoMessage)
                        else:
                            infoMessage = f"startGradingRun: {test.type} is an unknown test type"
                            Loghelper.logInfo(infoMessage)

                        gradeResultList.append(gradeResult)

                        # Create a feedback object for the action
                        # TODO: better mechanismen for generating the id (if necessary at all)
                        feedbackItemid = len(feedbackItemList) + 1
                        feedbackItem = FeedbackItem(feedbackItemid, submission)
                        if checkstyleReportHtmlPath != "":
                            feedbackItem.checkstyleReportpath = checkstyleReportHtmlPath
                        if jUnitReportHtmlPath != "":
                            feedbackItem.jUnitReportpath = jUnitReportHtmlPath
                        if textcomparePath != "":
                            feedbackItem.textCompareReportpath = textcomparePath
                        feedbackItem.message = f"Points/Problems: {points}/{problemCount}"
                        # TODO: When high?
                        feedbackItem.severity = "normal"
                        feedbackItemList.append(feedbackItem)

                print(Fore.LIGHTCYAN_EX + f"*** Bewertung abgeschlossen - Anzahl Probleme: {problemCount} ***" + Style.RESET_ALL)

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
    # subprocess.call(["notepad.exe", actionReportPath])

    # write the xml report for the grading results
    gradeReportPath = xmlHelper.generateGradingResultReport(gradeResultList)
    # display report file
    # subprocess.call(["notepad.exe", gradeReportPath])

    # convert the grading results report to html
    htmlPath = xmlHelper.convertGradingResultReport2Html(gradeReportPath, gradeSemester, gradeModule, exercise)
    os.startfile(htmlPath)
    print(f"{submisssionsGraded} Submissions bearbeitet - OK: {okCount} Error: {errorCount}")

    # convert the feedback report to html
    feedbackReportPath = xmlHelper.generateFeedbackReport(feedbackItemList)
    htmlPath = xmlHelper.convertFeedbackReport2Html(feedbackReportPath, gradeSemester, gradeModule, exercise)
    os.startfile(htmlPath)

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

'''
Menue I - updates the simpelgrader.ini file or creates a new one
'''
def MenueI_setupSimpelgraderIni() -> None:
    # backup of the existing ini file
    # load every prompt from the txt file
    # test if an directory exists and offer a correction
    # store the ini file and run a precheck
    n = 1
    iniPath = os.path.join(os.getcwd(), "Simpelgrader.ini")
    # does the file already exists?
    if not os.path.exists(iniPath):
        with open(iniPath, mode="w", encoding="utf8") as fh:
            fh.write("[path]")
            fh.write("[run")
            fh.write("[start]")
    else:
        abbruch = False
        while not abbruch or n > 999:
            newIniPath = os.path.join(os.getcwd(), f"Simpelgrader_{n:03d}.ini")
            if not os.path.exists(newIniPath):
                abbruch = True
                continue
            n += 1
        shutil.copy(iniPath, newIniPath)
        infoMessage = f"setupSimpelgraderIni: copied {iniPath} to {newIniPath}"
        Loghelper.logInfo(infoMessage)

    config = configparser.ConfigParser()
    config.read(iniPath)
    txtpromptsPath = "SimpelgraderSetupPrompts.txt"
    changeFlag = False
    with open(txtpromptsPath, mode="r", encoding="utf8") as fh:
        promptLines = fh.readlines()
        print("*** Eingabe auslassen per Enter-Taste ***")
        # strip the / from the last line
    for promptLine in [pl if pl[-1] != "\n" else pl[:-1] for pl in promptLines if pl != ""]:
        promptElements = promptLine.split(",")
        prompt = promptElements[0]
        section = promptElements[1]
        entry = promptElements[2]
        try:
            promptInput = input(f"{prompt} (currently {config[section][entry]})\n")
            if promptInput != "":
                config[section][entry] = promptInput
                changeFlag = True
        except Exception as ex:
            infoMessage = f"setupSimpelgraderIni: error accessing {iniPath} with section={section}/entry={entry}"
            Loghelper.logError(infoMessage)

    # save everything in the config file again
    if changeFlag:
        with open(iniPath, mode="w", encoding="utf8") as fh:
            config.write(fh)
            infoMessage = f"setupSimpelgraderIn: updated settings in {iniPath}"
            Loghelper.logInfo(infoMessage)
            print("*** Simpelgrader.ini wurde aktualisiert ***")
            # Re-initialize the variables
            initVariables()

# =============================================================================
# Starting point
# =============================================================================

'''
Main function for the application
'''
def start() -> None:
    initApp()
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
        elif choice == "H":                 # Show the current log file
            MenueH_showLogfile()
        elif choice == "I":
            MenueI_setupSimpelgraderIni()   # Allow preparting a simpelgrader.ini
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
