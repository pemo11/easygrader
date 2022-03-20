# =============================================================================
# Automatisiertes Bewerten von Java-Programmieraufgaben
# Erstellt: 01/03/22
# Letztes Update: 20/03/22
# Version 0.40
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
from XmlHelper import XmlHelper
import JavaHelper
import DBHelper

# =============================================================================
# Globale Variablen
# =============================================================================
appVersion = "0.40"
appName = "SimpleGrader"
taskBasePath = ""
submissionPath = ""
# Dieser Pfad enthält die ausgepackten Zip-Archive
submissionDestPath = ""
gradingPlanPath = ""
studentRosterPath = ""
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
    config.read("Simplegrader.ini")
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
# Main Menue
# =============================================================================

'''
Shows the Welcome Banner
'''
def showBanner():
    print(Fore.LIGHTGREEN_EX + "*" * 80)
    print(f"{'*' * 24}{f' Welcome to Simple Grader {appVersion} '}{'*' * 25}")
    print("*" * 80 + Style.RESET_ALL)

'''
Shows application main menue
'''
def showMenu():
    menuList = []
    menuList.append("Alle Abgaben extrahieren")
    menuList.append("Alle Abgaben anzeigen")
    menuList.append("Vollständigkeitscheck für Abgaben")
    menuList.append("Alle Abgaben eines Studenten anzeigen")
    menuList.append("Alle Studenten ohne Abgaben anzeigen")
    menuList.append(Fore.LIGHTYELLOW_EX + "Bewertungsdurchlauf starten" + Style.RESET_ALL)
    menuList.append("Alle Bewertungsdurchläufe anzeigen")
    menuList.append("Alle Bewertungen anzeigen")
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
Extracts all submission files
This methods is always run first to make the submissions accessible for grading and 
other operations
'''
def extractSubmissions():
    submissionCount = ZipHelper.extractSubmissions(submissionPath, submissionDestPath)
    infoMessage = f"{submissionCount} Abgaben erfolgreich nach {submissionDestPath} extrahiert"
    Loghelper.logInfo(infoMessage)
    print(infoMessage)
    # Stores all submissions in the database
    storeSubmissions()

'''
Stores all submissions in the database
'''
def storeSubmissions():
    # delete all previous submissions
    DBHelper.clearAllSubmission(dbPath)
    submissionCounter = 0
    dicSubmissions = getSubmissions()
    for exercise in dicSubmissions:
        for student in dicSubmissions[exercise]:
            timestamp = datetime.datetime.now()
            try:
                DBHelper.storeSubmission(dbPath, timestamp, gradeSemester, gradeModule, exercise, student, False)
                submissionCounter += 1
            except Exception as ex:
                infoMessage = f"Submission für Semester={gradeSemester} Modul={gradeModule} Exercise={exercise} Student={student} konnte nicht in der Datenbank gespeichert werden. ({ex})"
                Loghelper.logError(infoMessage)
    infoMessage = f"{submissionCounter} Abgaben wurden in der Datenbank gespeichert."
    Loghelper.logInfo(infoMessage)
    print(f"*** {infoMessage} ***")

'''
Outputs all submissions
'''
def showSubmissions():
    dicSubmissions = getSubmissions()
    # go through all exercises
    for exercise in dicSubmissions:
        print(f"Abgaben für {exercise}")
        for student in dicSubmissions[exercise]:
            print(f">> {student}")
            for file in dicSubmissions[exercise][student]:
                print(f">>> {file}")

'''
Check for missing submissions of all students
*** Neu machen über Datenbankabfrage !
'''
def showMissingSubmissions():
    # key= exercise - values=dic with student as key and files as value
    dicSubmissions = getSubmissions()
    # Hole ein dic mit Student als key und einem dic mit exercise als key und den files als values
    # exerciseTupels = [(ex, dicSubmissions[ex]) for ex in dicSubmissions]
    dicStudents = {}
    for exercise in dicSubmissions:
        for student in dicSubmissions[exercise]:
            if dicStudents.get(student) == None:
                dicStudents[student] = [{exercise:dicSubmissions[exercise][student]}]
            else:
                dicStudents[student].append({exercise:dicSubmissions[exercise][student]})

    dicRoster = getStudentRoster(studentRosterPath)
    for student in dicRoster:
        studentName = student.replace("_", " ")
        if dicStudents.get(student) == None:
            print(f"*** Student: {studentName} - bislang keine Abgaben!")
        else:
            # Alle Exercises durchgehen
            for exerciseDic in dicStudents[student]:
                if len(dicStudents[student]) == 0:
                    for exercise in exerciseDic:
                        print(f"*** Student: {studentName} - bislang keine Abgaben!")
                else:
                    for exercise in exerciseDic:
                        files = ",".join([f for f in dicSubmissions[exercise][student]])
                        print(f"*** Student: {studentName} - Abgaben für {exercise}: {files}")
                        # TODO: Vergleichen mit den durchgeführten Abgaben
                        studentSubmissions = [s for s in dicRoster[student] if s == "1"]


    '''
    for exercise, students in exerciseTupels:
        print(f"Abgaben für Aufgabe {exercise}")
        for student in students:
            print(f">> {student}")
        if dicSubmissions.get(student) == None:
            print(f"*** Keine Submissions von {studentName} ***")
        else:
            submissions = [s for s in dicRoster[student] if s == "1"]
            print(f"*** Student {studentName} {len(submissions)} von {len(dicSubmissions[student])} bewertet")
    '''

'''
Output all submissions for a student by name 
'''
def showSubmissionsByStudent():
    studentName = input("Name des Studenten?")
    # Name etwas aufbereiten, da die Namen als Vorname_Nachname abgelegt sind
    studentName = studentName.replace(" ", "_")
    dic = getSubmissions()
    if dic.get(studentName):
        print(f"Abgaben von {studentName}")
        for exercise in dic[studentName]:
            print(f">> {exercise}")
    else:
        print(f"Keine Abgaben von {studentName}")
        # TODO: Später auch alternative Namen anzeigen

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
Shows all students without submissions for single assigments
'''
def showStudentsWithoutSubmission(csvPath):
    dicSubmissions = getSubmissions()
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
            infoMessage = f"!!! Missing files in Submission {zipPath}: {','.join(missingFiles)} !!!"
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

    htmlPath = xmlHelper.generateHtmlReport(gradeReportPath, gradeSemester, gradeModule, gradeExercise)
    os.startfile(htmlPath)
    print(f"{len(submissions)} Submissions bearbeitet - OK: {okCount} Error: {errorCount}")

# =============================================================================
# Helper functions
# =============================================================================

'''
Get all student submissions from the dest submission directory with the extracted files
Returns a dic of submission objects with exercise als key

Assumes each submission file name:
EA1_A_PMonadjemi.zip
EA1_B_PMonadjemi.zip
or
EA1_PMonadjemi.zip
in this case default level A is assumed
'''
def getSubmissions():
    submissionDic = {}
    for tEntry in os.walk(submissionDestPath):
        if len(tEntry[2]) > 0:
            basePath = tEntry[0]
            student = os.path.basename(basePath)
            exercise =tEntry[0].split("\\")[-2]
            if submissionDic.get(exercise) == None:
                submissionDic[exercise] = {}
            if submissionDic[exercise].get(student) == None:
                submissionDic[exercise][student] = []
            for file in tEntry[2]:
                submissionDic[exercise][student].append(file)
    return submissionDic

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
Main starting point
'''
def start():
    initVariables()
    infoMessage = f"Starting SimpleGrader (Version {appVersion}) - executing {gradingPlanPath}"
    Loghelper.logInfo(infoMessage)

    # for coloured output
    colorama.init()

    showBanner()

    # Create database
    if not os.path.exists(dbPath):
        DBHelper.initDb(dbPath)

    exitFlag = False
    while not exitFlag:
        choice = showMenu().upper()
        if choice == "Q":
            exitFlag = True
        elif choice == "A":                 # Alle Abgaben extrahieren
            extractSubmissions()
        elif choice == "B":                 # Alle Abgaben anzeigen
            showSubmissions()
        elif choice == "C":                 # Vollständigkeitscheck
            showMissingSubmissions()
        elif choice == "D":                 # Alle Abgaben eines Studenten anzeigen
            showSubmissionsByStudent()
        elif choice == "E":                 # Studenten ohne Abgaben anzeigen
            showStudentsWithoutSubmission(studentRosterPath)
        elif choice == "F":                 # Grading-Run starten
            startGradingRun()
        elif choice == "G":                 # Alle Grading-Runs anzeigen
            showGradingRuns()
        elif choice == "H":                  # Alle Gradings anzeigen
            showGradings()
        elif choice == "I":                 # Alle Gradings eines Studenten anzeigen
            showGradingsByStudent()
        else:
            print(f"!!! {choice} ist eine relativ unbekannte Auswahl !!!")

# Starting point
if __name__ == "__main__":
    start()

