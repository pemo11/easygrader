# file: ZipHelper.py
import os
import zipfile
import tempfile
import shutil
import Loghelper
import re

from SubmissionFile import SubmissionFile

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
Extracts a single zip file
'''
def extractArchive(zipPath, destPath) -> int:
    fileCount = 0
    try:
        with zipfile.ZipFile(zipPath, mode="r") as fh:
            fh.extractall(destPath)
        fileCount = len([fi for fi in os.listdir(destPath) if not fi.endswith("zip")])
    except Exception as ex:
        infoMessage = f"extractArchive - error {ex}"
        Loghelper.logError(infoMessage)
    infoMessage = f"extractArchive - {fileCount} files extracted"
    Loghelper.logInfo(infoMessage)
    return fileCount

