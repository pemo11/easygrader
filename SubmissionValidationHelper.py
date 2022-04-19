# file: SubmissionValidationHelper.py

'''
Contains several functions for dealing with submission errors
A submission error is something like a missing file or an archive name that does not adhere to the name schema
'''

submissionValidationList = []

'''
Add a new submission validation entry to the list
'''
def addSubmissionValidation(entry):
    submissionValidationList.append(entry)

'''
Gets the whole list of submission validation entries
'''
def getSubmissionValidation():
    return submissionValidationList

