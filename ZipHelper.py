# file: ZipHelper.py
import os
import zipfile
import tempfile
import shutil
import Loghelper
import re

from SubmissionFile import SubmissionFile

'''
Extract zip file in the temp directory
'''
def extractSubmissions1(destPath, zipPath):
    zipCounter = 0
    baseName = os.path.basename(zipPath).split(".")[0]
    # get module name (again non greedy)
    # modPattern = "^(\\w*?)_"
    # modName = re.findall(modPattern, zipName)[0]
    # directory has already been created
    # modPath = os.path.join(tempfile.gettempdir(), modName)
    # EA1_Dirk_Grasekamp.zip
    # studPattern = "^(\\w*?)_(.*).zip"
    # studName = re.findall(studPattern, zipName)[0][1]
    tmpDirPath = os.path.join(destPath, baseName)
    if not os.path.exists(tmpDirPath):
        os.mkdir(tmpDirPath)
        infoMessage = f"ZipHelper-> Verzeichnis {tmpDirPath} angelegt"
        Loghelper.logInfo(infoMessage)
    # extract all files
    with zipfile.ZipFile(zipPath) as zp:
        zp.extractall(destPath)

    infoMessage = f"ZipHelper-> {zipPath} extrahiert"
    Loghelper.logInfo(infoMessage)
    return tmpDirPath

    # extract all the other zip files in the same directory
    for f in os.listdir(tmpDirPath):
        if f.endswith("zip"):
            zipCounter += 1
            zipPath = os.path.join(destPath, f)
            with zipfile.ZipFile(zipPath) as zp:
                zp.extractall(destPath)
                infoMessage = f"ZipHelper-> {zipPath} extrahiert"
                Loghelper.logInfo(infoMessage)
            # delete zip file in the temp directory
            os.remove(zipPath)
            infoMessage = f"ZipHelper-> {zipPath} gelöscht"
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
def extractSubmissions2(submissionPath, destPath):
    # enumerates every submission file
    for file in [fi for fi in os.path.listdir(submissionPath) if fi.endswith("zip")]:
        submissionFile = SubmissionFile(file)
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
