# file: JavaFileHelper.py

import os
import re

def getAuthorName(javaPath):
    pass

def getMatricleId(javaPath):
    commentFlag = False
    matricleId = ""
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
                matricleText = re.findall(authorPattern, line)[0]
                # pattern for the matriculation id
                matriclePattern = "Matrikel-Nr:\s*(\d+)"
                if len(re.findall(matriclePattern, matricleText)) > 0:
                    matricleId = re.findall(matriclePattern, matricleText)[0]
                break
        return matricleId

