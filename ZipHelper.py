# file: ZipHelper.py
import os
import zipfile
import tempfile
import shutil

import DBHelper
import Loghelper
import re

import Main
from SubmissionName import SubmissionName
from Submission import Submission

'''
Extracts a single zip file
'''
def extractArchive(zipPath, destPath) -> int:
    fileCount = 0
    try:
        with zipfile.ZipFile(zipPath, mode="r") as fh:
            fh.extractall(destPath)
        # exclude zip files
        fileCount = len([fi for fi in os.listdir(destPath) if not fi.endswith("zip")])
    except Exception as ex:
        infoMessage = f"extractArchive - error {ex}"
        Loghelper.logError(infoMessage)
    infoMessage = f"extractArchive - {fileCount} files extracted to {destPath}"
    Loghelper.logInfo(infoMessage)
    return fileCount

'''
extract all submission files into directories for each submission containing the files
the directory is unique if two internal zip files have the same name
'''
def unzipAll(zipPfad, destFolder, fileCount) -> int:
    if not os.path.exists(zipPfad):
        return fileCount
    with zipfile.ZipFile(zipPfad, mode="r") as zh:
        # get only file names without extension if it exists
        zipDirs = [d.split(".")[0] for d in zh.namelist()]
        # get the name of all sub directories in the temp directory
        dirNames= [d for d in os.listdir(destFolder) if os.path.isdir(os.path.join(destFolder, d))]
        # any sub dirs?
        if len(dirNames) > 0:
            # go through all sub directories
            for zipDir in zipDirs:
                # directory already exists?
                if zipDir in dirNames:
                    # change the name by adding an appendix like _001
                    n = 1
                    newDirPath = os.path.join(destFolder, f"{zipDir}_{n:03d}")
                    oldDirPath = os.path.join(destFolder, zipDir)
                    # rename by moving the directory
                    shutil.move(oldDirPath, newDirPath)
        # extract current zip file
        zh.extractall(path=destFolder)
    # delete current zip file
    os.remove(zipPfad)
    # go through all the files of the extracted zip file
    for root, dirs, files in os.walk(destFolder):
        # only consider the files this time
        for filename in files:
            # is it another zip file?
            if filename.endswith("zip"):
                # the full path of the zip file
                zipPath = os.path.join(root, filename)
                # extract this zip file too with the current file count
                unzipAll(zipPath, root, fileCount)
            else:
                # if its a normal file just increment the file count
                fileCount += 1
    # return file count
    return fileCount

'''
extracts all submissions inside a single zip file and returns a dict
dict -> exercise key -> dict -> unique student name key -> list of submisssions
'''
def extractSubmissions(dbPath, zipPfad, destPath) -> dict:
    fileCount = unzipAll(zipPfad, destPath, 0)
    infoMessage = f"extractSubmissions: {fileCount} files extracted"
    Loghelper.logInfo(infoMessage)
    folderDic = {}
    submissionId = 1
    # go through all subdirs
    for zipDir in os.listdir(destPath):
        exercise = zipDir.split("_")[0]
        studentName = "_".join(zipDir.split("_")[1:])
        if folderDic.get(exercise) == None:
            folderDic[exercise] = {}
        if folderDic[exercise].get(studentName) == None:
            folderDic[exercise][studentName] = []
        zipPath = os.path.join(destPath, zipDir)
        fileNames = ",".join(os.listdir(zipPath))
        studentId = DBHelper.getStudentId(dbPath, studentName)
        submission = Submission(submissionId, studentId)
        submission.exercise = exercise
        submission.files = fileNames
        submissionId += 1
        folderDic[exercise][studentName].append(submission)

    return folderDic
