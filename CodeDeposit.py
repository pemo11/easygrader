'''
All the old functions that are not in use anymore but took a lot of time and creativity to code
'''

'''
Gets the content of the roster file (CSV)
returns a dic with the student name as key and a (exercise,value) tuple
Currently not in use
'''
def getStudentRoster(csvPath):
    dic = {}
    with open(csvPath, encoding="utf-8") as fh:
        csvReader = csv.reader(fh)
        # Immer wieder genial
        keys = next(fh).split(",")[1:]
        # Letztes \n abtrennen
        keys[-1] = keys[-1].strip()
        for row in csvReader:
            name = row[0].replace(" ", "_")
            dic[name] = {}
            for i, exercise in enumerate(row[1:-1]):
                if dic[name].get(keys[i]) == None:
                    dic[name][keys[i]] = []
                dic[name][keys[i]].append(exercise)
    return dic

'''
Get the submissions by exercise
not in use anymore but a good exercise for how to use lists and dics
'''
def getSubmissionByStudent():
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
    return dicStudents


'''
Updates the student roster with the submissions from the database
Instead of overwriting the updated csv file gets an index like _001,002 etc
so WS2122_GP1_Studenten.csv -> WS2122_GP1_Studenten_001.csv
and WS2122_GP1_Studenten_001.csv -> WS2122_GP1_Studenten_002.csv
max is 999 which should never be a problem
Update: 14/04/22 - es soll doch alles datenbankbasiert sein
Und ich hatte mir mi den Dateinamen und den Nummer so viel Arbeit gemacht;)
'''
def updateStudentRoster():
    studentRosterDir = os.path.dirname(studentRosterPath)
    studentRosterFile = os.path.basename(studentRosterPath).split(".")[0]
    # get the max file name
    csvFiles = [int(re.match("_(\d+)", fi)[0]) if re.match("_(\d+)", fi) else None for fi in os.listdir(studentRosterDir) if fi.endswith("csv")]
    # remove all None values (not perfect solution - any ideas?)
    csvFiles = [fi for fi in csvFiles if fi != None]
    if len(csvFiles) == 0:
        studentRosterFileNew = f"{studentRosterFile}_001.csv"
        studentRosterFile += ".csv"
    elif len(csvFiles) == 1:
        maxRosterIndex = csvFiles[-1]
        studentRosterFileNew = f"{studentRosterFile}_{maxRosterIndex:03d}.csv"
        studentRosterFile += ".csv"
    else:
        maxRosterIndex = csvFiles[-1]
        max2RosterIndex = csvFiles[-2]
        studentRosterFileNew = f"{studentRosterFile}_{maxRosterIndex:03d}.csv"
        studentRosterFile =  f"{studentRosterFile}_{max2RosterIndex:03d}.csv"
    # Copy the old file to the new for the update
    csvSourcePath = os.path.join(studentRosterDir, studentRosterFile)
    csvDestPath = os.path.join(studentRosterDir, studentRosterFileNew)
    shutil.copy(csvSourcePath, csvDestPath)
    infoMessage = f"updateStudentRoster - copied {csvSourcePath} to {csvDestPath}"
    # Update the csv file destPath with the database
    # TODO !!!

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
uses the file system files
'''
def showMissingSubmission():
    dicRoster = getStudentRoster(studentRosterPath)
    for student in dicRoster:
        # studentName = student.replace("_", " ")
        submissions = DBHelper.getSubmissionByStudent(dbPath, student)
        if len(submissions) == 0:
            print(f"*** Student: {student} - bislang keine Abgaben!")
        else:
            # Alle Exercises durchgehen
            for exercise in dicRoster[student]:
                if len(dicRoster[student]) == 0:
                    print(f"*** Student: {student} - bislang keine Abgaben!")
                else:
                    exerciseDic = dicRoster[student]
                    for exercise in exerciseDic:
                        files = ",".join([f for f in dicRoster[exercise][student]])
                        print(f"*** Student: {student} - Abgaben für {exercise}: {files}")
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
Shows all students without submissions for single assigments
'''
def showStudentsWithoutSubmission():
    dicSubmissions = getSubmissions()
    dicRoster = getStudentRoster()
    for student in dicRoster:
        studentName = student.replace("_", " ")
        if dicSubmissions.get(student) == None:
            print(f"*** Keine Submissions von {studentName} ***")
        else:
            submissions = [s for s in dicRoster[student] if s == "1"]
            print(f"*** Student {studentName} {len(submissions)} von {len(dicSubmissions[student])} bewertet")

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
store submissions in the database
'''
def storeSubmissions() -> None:
    # delete all previous submissions
    DBHelper.clearAllSubmission(dbPath)
    submissionCounter = 0
    # get all submissions from the file system - key = exercise
    dicSubmissions = getSubmissions()
    for exercise in dicSubmissions:
        for studentId in dicSubmissions[exercise]:
            timestamp = datetime.datetime.now().strftime("%d.%m.%y %H:%M")
            try:
                result = DBHelper.storeSubmission(dbPath, timestamp, gradeSemester, gradeModule, exercise, studentId, False)
                if result != -1:
                    submissionCounter += 1
                    infoMessage = f"submission for student {studentId} successfully stored in database"
                    Loghelper.logInfo(infoMessage)
                else:
                    infoMessage = f"submission for student {studentId} could not be stored in database"
                    Loghelper.logError(infoMessage)
            except Exception as ex:
                result = DBHelper.getStudentById(studentId)
                student = result[0] if len(result > 0) else ""
                infoMessage = f"submission for semester={gradeSemester} module={gradeModule} exercise={exercise} and student={student} could not store in the database ({ex})"
                Loghelper.logError(infoMessage)
    infoMessage = f"{submissionCounter} submissions were stored in the database"
    Loghelper.logInfo(infoMessage)
    print(f"*** {infoMessage} ***")

    # put all current submissions in a dict
    submissionDic2 = {}
    for submissionDir in [d for d in os.listdir(submissionDestPath) if d != "rejects"]:
        submission = SubmissionFile(submissionDir)
        exercise = submission.exercise
        if submissionDic.get(exercise) == None:
            submissionDic[exercise] = []
        student = submission.student
        submissionDic[exercise].append(student)

'''
Gets all submissions from the database
'''
def getSubmissions() -> dict:
    submissionDic = DBHelper.getSubmissions(dbPath)
    print(submissionDic)

'''
extracts the submission for a single exercise downloaded from Moodle
eg. Java 1-Einsendeaufgabe zur Lektion 4-35.zip
contains Sebastian Student_3_assignsubmission_file_, Sebastian Student_5_assignsubmission_file_ etc
as sub directories (not zip files)
'''
def extractSingleSubmission(exercise) -> dict:
    # extract zip file with all the submission zip files
    zipFiles = [fi for fi in os.listdir(submissionPath) if fi.endswith("zip")]
    # only one zip file allowed
    if len(zipFiles) != 1:
        infoMessage = f"extractSubmissions: exactly one zip file expected in {submissionPath}"
        Loghelper.logError(infoMessage)
        return None
    zipPath = os.path.join(submissionPath, zipFiles[0])

    # extract main submission zip as directories
    ZipHelper.extractArchive(zipPath, submissionDestPath)

    # start over with the extracted directories
    submissionProcessedCount = 0
    # delete all previous submissions
    DBHelper.clearAllSubmission(dbPath)

    fileCount = 0
    fileErrorCount = 0

    # Process all submissions directories but leave out the rejects dir
    for submissionDir in [d for d in os.listdir(submissionDestPath) if d != "rejects"]:
        # get student name
        studnamePattern = "([\w\s]+)_(\d+)_"
        if not re.match(studnamePattern, submissionDir):
            infoMessage = f"extractSingleSubmission: {submissionDir} does not match name pattern"
            Loghelper.logError(infoMessage)
            continue
        studentName = re.match(studnamePattern, submissionDir).group(1)
        # get student id for the name
        studentIdList = DBHelper.getStudentIdList(dbPath, studentName)
        if studentIdList == None or len(studentIdList) == 0:
            infoMessage = f"extractSingleSubmission: no studentId for {studentName} found"
            Loghelper.logError(infoMessage)
            continue
        if len(studentIdList) == 1:
            studentId = studentIdList[0]
            infoMessage = f"extractSingleSubmission: studentId {studentId} assigned to {studentName}"
            Loghelper.logInfo(infoMessage)
        else:
            infoMessage = f"extractSingleSubmission: multiple Ids for {studentName} found"
            Loghelper.logInfo(infoMessage)
            # get student id later from java file
            studentId = -1

        # extract the zip file in the directory - this must follow the name pattern eg. EA1A_Name1_Name2.zip
        filePattern = "(\w+)_(\w+)_(\w+)\.zip"
        fileErrorCount = 0

        submissionDirPath = os.path.join(submissionDestPath, submissionDir)

        # get the zip file
        zipFiles = [fi for fi in os.listdir(submissionDirPath) if fi.endswith("zip")]
        # should not happen
        if len(zipFiles) == 0:
            infoMessage = f"extractSingleSubmission: directory {submissionDirPath} has no content"
            Loghelper.LogError(infoMessage)
            continue
        zipFilename = zipFiles[0]
        zipPath = os.path.join(submissionDirPath, zipFilename)
        ZipHelper.extractArchive(zipPath, submissionDirPath)

        fileCount += 1
        submisionName = SubmissionName(zipFilename)

        # delete submission zip file in temp directory
        # os.remove(zipPath)

        fileNotValid = False
        # does the filename matches the pattern?
        fileNotValid = not re.match(filePattern, zipFilename)
        if fileNotValid:
            infoMessage = f"extractSingleSubmission: {zipFilename} does not match name pattern"
            Loghelper.logError(infoMessage)
        else:
            # check if the zip file only contains at least one file but not directories
            fiZip = zipfile.ZipFile(zipPath)
            fileNotValid = len(fiZip.namelist()) == 0 or len([f for f in fiZip.namelist() if len(f.split("/")) > 1]) > 0
            if fileNotValid:
                infoMessage = f"extractSingleSubmission: {zipFilename} does not contains files or contains directories"
                Loghelper.logError(infoMessage)
            # to prevent PermissionErrors
            fiZip.close()
        # if file is not valid move file to special directory
        if fileNotValid:
            rejectDirPath = os.path.join(submissionDestPath, "rejects")
            if not os.path.exists(rejectDirPath):
                os.mkdir(rejectDirPath)
                infoMessage = f"extractMoodleSubmissions: {rejectDirPath} directory created"
                Loghelper.logInfo(infoMessage)
            fileErrorCount += 1
            # Move fi to the rejects directory
            if not os.path.exists(os.path.join(rejectDirPath, zipFilename)):
                shutil.move(zipPath, rejectDirPath)
                infoMessage = f"extractMoodleSubmissions: {zipFilename} moved to {rejectDirPath}"
                Loghelper.logInfo(infoMessage)
        if fileErrorCount > 0:
            infoMessage = f"extractMoodleSubmissions: {fileErrorCount} of {fileCount} does not match name pattern"
            Loghelper.logError(infoMessage)

        # if no studentid found because of identical student names get the studentid from a java file
        if studentId == -1:
            studentIdList = []
            for fi in [f for f in os.listdir(submissionDirPath)]:
                if len(fi.split(".")) > 0 and fi.split(".")[1].lower() == "java":
                    javaFilePath = os.path.join(submissionDirPath, fi)
                    studentId = JavaFileHelper.getStudentId(javaFilePath)
                    if studentId and studentId != "":
                        studentIdList.append(studentId)
            # did a java file contained a studentId?
            if len(studentIdList) > 0:
                studentId = -1
                # check if all ids are valid
                for id in studentIdList:
                    if DBHelper.getStudentById(dbPath, id) != None:
                        studentId = id
                        break
                # no valid id?
                if studentId == -1:
                    infoMessage = f"extractMoodleSubmissions: no valid studentId in {submissionDir} files"
                    Loghelper.logError(infoMessage)
                    continue
        # get the name of all files as string
        files = ",".join(os.listdir(submissionDirPath))
        timestamp = datetime.now()
        DBHelper.storeSubmission(dbPath, timestamp, gradeSemester, gradeModule, exercise, studentId, files, False)
        submissionProcessedCount += 1

    infoMessage = f"{submissionProcessedCount} submissions stored in the database."
    Loghelper.logInfo(infoMessage)

    # return value is a dictionary with exercise as a key for a dict with student as key for each submission
    dic = DBHelper.getSubmissions(dbPath)
    # return dictionary to the caller
    return dic

'''
extract all submissions for a single submission and store them in the database
assumes that the single zip file contains only submissions for a single exercise
important: the file names only contains the student name and can be ambigious
'''
def processSingleSubmission() -> None:
    global submissionDic
    exercise = input("Name der Übung (z.B. EA1)?")
    # validate the roster file first
    if not RosterHelper.validateRoster(studentRosterPath):
        # roster file is not valid exit
        return

    # Store the complete student roster in the database
    RosterHelper.saveRosterInDb(dbPath, gradeSemester, gradeModule, studentRosterPath)

    # extract the submissions from the downloaded zip file
    submissionDic = extractSingleSubmission(exercise)

    # flatten a list of lists and get the element count
    submissionCount = len([item for sublist in [submissionDic[k] for k in submissionDic] for item in sublist])
    infoMessage = f"{submissionCount} submissions for {len(submissionDic)} exercise extracted from the Moodle zip file"
    Loghelper.logInfo(infoMessage)


'''
Extracts all submissions in the dest directory and "flattens" zip files that contains zip file
dest directory:
-temp
--module (eg. GP1)
---exercise (eg. EA1)
----studentname (eg. Dirk_Grasekamp)
-----app.java
-----testapp.java
-----etc

'''
def extractSubmissions(submissionPath, destPath):
    # enumerates every submission file
    submissionCount = 0
    for file in [fi for fi in os.listdir(submissionPath) if fi.endswith("zip")]:
        submissionCount += 1
        submissionFile = SubmissionName(file)
        exercise = submissionFile.exercise
        exercisePath = os.path.join(destPath, exercise)
        # Create exercise path for the first exercise
        if not os.path.exists(exercisePath):
            os.mkdir(exercisePath)
            infoMessage = f"directory {exercisePath} created"
            Loghelper.logInfo(infoMessage)
        student = submissionFile.student
        studentPath = os.path.join(exercisePath, student)
        # Create a student path for the student files
        if not os.path.exists(studentPath):
            os.mkdir(studentPath)
            infoMessage = f"directory {studentPath} created"
            Loghelper.logInfo(infoMessage)
        # Expand the archive
        zipPath = os.path.join(submissionPath, file)
        # Get all the files from the zip archive
        with zipfile.ZipFile(zipPath) as zp:
            for entry in zp.namelist():
                filename = os.path.basename(entry)
                # if its a directory no action
                if not filename:
                    continue
                # get the source file
                source = zp.open(entry)
                # create the destination file
                target = open(os.path.join(studentPath, filename), "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
                    infoMessage = f"{filename} extracted to {studentPath}"
                    Loghelper.logInfo(infoMessage)
    return submissionCount

'''
Extract each submission zip file into its own directory
'''
def extractSubmissionZips(submissionDestPath, deleteZip=False) -> int:
    fileCount = 0
    for fiZip in [fi for fi in os.listdir(submissionDestPath) if fi.endswith("zip")]:
        fiZipPath = os.path.join(submissionDestPath, fiZip)
        fiFilename = fiZip.split(".")[0]
        destPath = os.path.join(submissionDestPath, fiFilename)
        fileCount += extractArchive(fiZipPath, destPath)
        # delete zip?
        if deleteZip:
            os.remove(fiZipPath)
            infoMessage = f"extractSubmissionZips: {fiZipPath} deleted"
            Loghelper.logInfo(infoMessage)
    return fileCount

'''
Extracts all submission files downloaded from Moodle
This methods is always run first to make the submissions accessible for grading and 
other operations
Update: Its based on the fact that the Moodle download is a single zip file that contains
another submission zip file which finally contains the submitted (zip) file
the submission directory contains only one zip file, eg moodle_Submission_110422.zip
'''
def extractMoodleSubmissions() -> dict:
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
    # check all files (not directories) if they match the name pattern for a submission zip file
    for fi in [f for f in os.listdir(submissionDestPath) if os.path.isfile(os.path.join(submissionDestPath, f))]:
        fileNotValid = False
        # does the filename matches the pattern?
        filePath = os.path.join(submissionDestPath, fi)
        fileNotValid = not re.match(filePattern, fi)
        if fileNotValid:
            infoMessage = f"extractMoodleSubmissions: {fi} does not match name pattern"
            Loghelper.logError(infoMessage)
        else:
            # check if the zip file only contains at least on file but not directories
            zipFi = zipfile.ZipFile(filePath)
            fileNotValid = len(zipFi.namelist()) == 0 or len([f for f in zipFi.namelist() if len(f.split("/")) > 1]) > 0
            if fileNotValid:
                infoMessage = f"extractMoodleSubmissions: {fi} does not contains files or contains directories"
                Loghelper.logError(infoMessage)
            # to prevent PermissionError
            zipFi.close()
        # if file is not valid move file to special directory
        if fileNotValid:
            rejectDirPath = os.path.join(submissionDestPath, "rejects")
            if not os.path.exists(rejectDirPath):
                os.mkdir(rejectDirPath)
                infoMessage = f"extractMoodleSubmissions: {rejectDirPath} directory created"
                Loghelper.logInfo(infoMessage)
            fileErrorCount += 1
            # Move fi to the rejects directory
            if not os.path.exists(os.path.join(rejectDirPath, fi)):
                shutil.move(filePath, rejectDirPath)
                infoMessage = f"extractMoodleSubmissions: {fi} moved to {rejectDirPath}"
                Loghelper.logInfo(infoMessage)
    if fileErrorCount > 0:
        infoMessage = f"extractMoodleSubmissions: {fileErrorCount} of {fileCount} does not match name pattern"
        Loghelper.logError(infoMessage)

    # go through all extracted submission files and extract all submitted files
    # submissionCount = ZipHelper.extractSubmissions(submissionDestPath, submissionDestPath)
    # Extract each submission zip file into its own directory
    submissionFileCount = ZipHelper.extractSubmissionZips(submissionDestPath)
    infoMessage = f"extractSubmissions - {submissionFileCount} submissions files successfully extracted to {submissionDestPath}"
    Loghelper.logInfo(infoMessage)

    # delete all zip files
    for fiZip in [fi for fi in os.listdir(submissionDestPath) if fi.endswith("zip")]:
        fiPath = os.path.join(submissionDestPath, fiZip)
        os.remove(fiPath)
        infoMessage = f"extractSubmissions - {fiZip} deleted"
        Loghelper.logInfo(infoMessage)

    # start over with the extracted directories
    submissionProcessedCount = 0

    # delete all previous submissions
    DBHelper.clearAllSubmission(dbPath)

    # Process all submissions directories but leave out the rejects dir
    for submissionDir in [d for d in os.listdir(submissionDestPath) if d != "rejects"]:
        studentIdList = []
        submissionDirPath = os.path.join(submissionDestPath, submissionDir)
        # for fi in [f for f in os.listdir(submissionDirPath) if os.path.isfile(os.path.join(submissionDirPath, f))]:
        for fi in [f for f in os.listdir(submissionDirPath)]:
            if len(fi.split(".")) > 0 and fi.split(".")[1].lower() == "java":
                javaFilePath = os.path.join(submissionDirPath, fi)
                # get the studentid from java file
                studentId = JavaFileHelper.getStudentId(javaFilePath)
                if studentId != "":
                    studentIdList.append(studentId)
        # studentId in one of the java files?
        if len(studentIdList) > 0:
            # studentId = studentIdList[0]
            studentId = -1
            # check if all ids are valid
            for id in studentIdList:
                if DBHelper.getStudentById(dbPath, id) != None:
                    studentId = id
                    break
            # no valid id?
            if studentId == -1:
                infoMessage = f"extractMoodleSubmissions: no valid studentId in {submissionDir} files"
                Loghelper.logError(infoMessage)
                # get student id by student name
                studentId = DBHelper.getStudentId(dbPath, submission.student)
                if studentId == None:
                    infoMessage = f"extractMoodleSubmissions: no valid studentId for {submission.student}"
                    Loghelper.logError(infoMessage)
        else:
            # get id of student from the database
            submission = SubmissionName(submissionDir)
            studentName = submission.student
            studentId = DBHelper.getStudentId(dbPath, studentName)
            if studentId == None:
                infoMessage = f"extractMoodleSubmissions: no valid studentId for {submission.student}"
                Loghelper.logError(infoMessage)

        # get the name of all files as string
        files = ",".join(os.listdir(submissionDirPath))
        submission = SubmissionName(submissionDir)
        exercise = submission.exercise
        timestamp = datetime.now()
        DBHelper.storeSubmission(dbPath, timestamp, gradeSemester, gradeModule, exercise, studentId, files, False)
        submissionProcessedCount += 1

    infoMessage = f"{submissionProcessedCount} submissions stored in the database."
    Loghelper.logInfo(infoMessage)

    # return value is a dictionary with exercise as a key for a dict with student as key for each submission
    dic = DBHelper.getSubmissions(dbPath)
    # return dictionary to the caller
    return dic
