# file: ZipHelper.py
import os
import zipfile
from zipfile import  ZipFile
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
        with ZipFile(zipPath, mode="r") as fh:
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
    with ZipFile(zipPfad, mode="r") as zh:
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
build dictionary from the extracted archive
'''
def buildSubmissionDic(dbPath, destPath) -> dict:
    folderDic = {}
    # go through all subdirs
    submissionId = 1
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
        submission.path = zipPath
        submission.state = "OK" if studentId > 0 else "No Student Id"
        submissionId += 1
        folderDic[exercise][studentName].append(submission)
    return folderDic

'''
extracts all submissions inside a single zip file and returns a dict
dict -> exercise key -> dict -> unique student name key -> list of submisssions
!!! this is the old version that should not be used in the future !!!
'''
def extractSubmissions(dbPath, zipPath, destPath) -> dict:
    fileCount = unzipAll(zipPath, destPath, 0)
    infoMessage = f"extractSubmissions: {fileCount} files extracted"
    Loghelper.logInfo(infoMessage)
    submissionId = 1

    folderDic = buildSubmissionDic(dbPath, destPath)

    return folderDic

    # go through all subdirs and build a dict
    '''
    folderDic = {}
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
        submission.path = zipPath
        submissionId += 1
        folderDic[exercise][studentName].append(submission)

    return folderDic
    '''

'''
extracts a zip file in the "new" Moodle zip format - return submission dic
'''
def extractNewSubmission(dbPath, zipPath, tmpPath) -> dict:

    # extract the content of the zip file
    with ZipFile(zipPath) as zh:
        zh.extractall(tmpPath)

    # delete the original zip file to avoid mixups
    os.remove(zipPath)

    zipDic = {}
    # go through all the zip files
    for ziFi in [fi for fi in os.listdir(tmpPath) if fi.endswith(".zip")]:
        destPath = os.path.join(tmpPath, ziFi)
        with ZipFile(destPath) as zh:
            # for the future: list of allowed extensions
            names = [fi for fi in zh.namelist() if fi.endswith(".java")]
            studDir = re.findall(r"file_([\w+_]+)\.zip", ziFi)[0]
            # exclude the module name
            studDir = "_".join(studDir.split("_")[1:])
            # get the exercise name
            exercise = studDir.split("_")[0]
            # take only the lastname_firstname without exercise
            # first char should be capital
            studName = "_".join([namePart.capitalize() for namePart in studDir.split("_")][1:])
            # path for the submission files subdirectory
            studPath = os.path.join(tmpPath, studDir)
            # create the sub directory if it does not exist
            if not os.path.exists(studPath):
                os.mkdir(studPath)
            # exercise already a key?
            if zipDic.get(exercise) == None:
                zipDic[exercise] = {}
            # studName already a key?
            if zipDic[exercise].get(studName) == None:
                zipDic[exercise][studName] = []
            # extract all files into the student directory
            for name in names:
                zh.extract(name, studPath)
        os.remove(destPath)

    # go through all the directories and disolve all sub directories
    for zipDir in os.listdir(tmpPath):
        studPath = os.path.join(tmpPath, zipDir)
        exercise = zipDir.split("_")[0]
        # studname without the exercise name
        studName = "_".join(zipDir.split("_")[1:])
        # capitalize last and firstname
        studName = "_".join([namePart.capitalize() for namePart in studName.split("_")])
        for studDirItem in os.listdir(studPath):
            studItemPath = os.path.join(studPath, studDirItem)
            if os.path.isdir(studItemPath):
                # Move all files to studPath
                for studItemFile in [fi for fi in os.listdir(studItemPath) if not fi.startswith("._")]:
                    studItemFilePath = os.path.join(studItemPath, studItemFile)
                    if os.path.isfile(studItemFilePath):
                        # move the file to the student directory
                        if not os.path.exists(studPath):
                            shutil.move(studItemFilePath, studPath)
                        # adjust the moved file path
                        studItemFilePathNew = os.path.join(studPath, os.path.basename(studItemFilePath))
                        # append the path of the file to file list of that student
                        zipDic[exercise][studName].append(studItemFilePathNew)
                    else:
                        # Some directories contain subdirectories instead of files
                        for studItemFile2 in [fi for fi in os.listdir(studItemFilePath) if not fi.startswith("._")]:
                            studItemFilePath2 = os.path.join(studItemFilePath, studItemFile2)
                            # move file from subdirectory to the student directory
                            if not os.path.exists(studPath):
                                shutil.move(studItemFilePath2, studPath)
                            # adjust the moved file path
                            studItemFilePath2New = os.path.join(studPath, os.path.basename(studItemFilePath2))
                            # add the whole path not only the file name
                            zipDic[exercise][studName].append(studItemFilePath2New)
                # remove the sub directory
                shutil.rmtree(studItemPath)
            else:
                # append the file to file list of that student
                zipDic[exercise][studName].append(studItemPath)

    # convert zipDic into a submissionDic
    submissionDic = {}
    submissionId = 1
    for exercise in zipDic:
        for studentName in zipDic[exercise]:
            exercise = zipDir.split("_")[0]
            # get the files for that submission
            studFiles = zipDic[exercise][studentName]
            # should not be necessary but you'll never know;)
            if len(studFiles) == 0:
                continue
            # get the directory path for the files
            filesPath = os.path.dirname(studFiles[0])
            fileNames = ",".join([os.path.basename(fi) for fi in studFiles])
            if submissionDic.get(exercise) == None:
                submissionDic[exercise] = {}
            if submissionDic[exercise].get(studentName) == None:
                submissionDic[exercise][studentName] = []
            # get the student id for the student name
            studentId = DBHelper.getStudentId(dbPath, studentName)
            # id found?
            if studentId == -1:
                infoMessage = f"extractNewSubmission: no id for student {studentName} found - Submission will be skipped"
                Loghelper.logWarning(infoMessage)
                continue
            # create a new submission with the student id
            submission = Submission(submissionId, studentId)
            # assign the exercise too
            submission.exercise = exercise
            # get the semester from the student file path
            # TODO: Test with MacOS/Linux
            submission.semester = re.findall("simpelgrader\\\\(\w+)\\\\", filesPath, re.IGNORECASE)[0]
            # get the module from the student file patht too
            submission.module = re.findall("simpelgrader\\\\\w+\\\\(\w+)", filesPath, re.IGNORECASE)[0]
            # set the directory path for the submision files
            submission.path = filesPath
            # set the names of the submission files
            submission.files = fileNames
            # increment the submission Id
            submissionId += 1
            # add the submission to the dict
            submissionDic[exercise][studentName].append(submission)

    return submissionDic

'''
extracts a submission zip file that contains a zip file for each submission - the zip file can contain another zip file, a directory or just files
'''
def extractNewSubmission2(dbPath, zipPath, tmpPath) -> dict:

    # extract the content of the zip file
    with ZipFile(zipPath) as zh:
        zh.extractall(tmpPath)

    # delete the original zip file to avoid mixups
    os.remove(zipPath)

    zipDic = {}