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
