# file: JavaFileHelper.py

import os
import re

'''
get the author name from the java file
'''
def getAuthorName(javaPath) -> str:
    commentFlag = False
    authorPattern = "@author\s+([\w\d\s]+)"
    author = ""
    with open(javaPath, mode="r", encoding="utf8") as fh:
        lineIter = iter(fh.readlines())
        # the assignment within while works only from Python 3.8 on
        while line := next(lineIter):
            if line.strip().startswith("/**"):
                commentFlag = True
                continue
            if line.strip().startswith("*/"):
                commentFlag = False
                break
            # check for the author tag
            if commentFlag and len(re.findall(authorPattern, line)) > 0:
                author = re.findall(authorPattern, line)[0]
                return  author
        return author

'''
Extracts the studentId from a java file
'''
def getStudentId(javaPath) -> int:
    commentFlag = False
    studentId = ""
    authorPattern = "@author\s+(.+)"
    with open(javaPath, mode="r", encoding="utf8") as fh:
        lineIter = iter(fh.readlines())
        # the assignment within while works only from Python 3.8 on
        while line := next(lineIter):
            if line.strip().startswith("/**"):
                commentFlag = True
                continue
            if line.strip().startswith("*/"):
                commentFlag = False
                break
            # check for the author tag
            if commentFlag and len(re.findall(authorPattern, line)) > 0:
                studentIdText = re.findall(authorPattern, line)[0]
                # pattern for the student id
                studentIdPattern = "Matrikel-Nr:\s*(\d+)"
                if len(re.findall(studentIdPattern, studentIdText)) > 0:
                    studentId = re.findall(studentIdPattern, studentIdText)[0]
                break
        return studentId

