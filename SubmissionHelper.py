# file: SubmissionHelper.py
import os

import ZipHelper
import Loghelper

'''
Stores all submissions into a database
'''
def storeSubmissions(submissionPath):
    for dir, subdirs, files in os.walk(submissionPath):
        pass

'''
Extracts all zip files inside a directory into another directory
'''
def extractSubmissions(submissionSource, submissionDest):
    submissionCount = ZipHelper.extractSubmissions(submissionSource, submissionDest)
    infoMessage = f"{submissionCount} Abgaben erfolgreich nach {submissionDest} extrahiert"
    Loghelper.logInfo(infoMessage)
    print(infoMessage)
    # Stores all submissions in the database
    storeSubmissions(submissionDest)


