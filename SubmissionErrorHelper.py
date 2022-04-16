# file: SubmissionErrorHelper.py

'''
Contains several functions for dealing with submission errors
A submission error is something like a missing file or an archive name that does not adhere to the name schema
'''

submissionErrorList = []

'''
Add a new submission error entry to the list
'''
def addSubmissionError(entry):
    submissionErrorList.append(entry)

'''
Gets the whole list of submission error entries
'''
def getSubmissionError():
    return submissionErrorList

