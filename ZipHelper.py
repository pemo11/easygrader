# file: ZipHelper.py

import os
import zipfile
import tempfile
import shutil

'''
Extract zip file in the temp directory
'''
def extractZip(zipPath):
    zipCounter = 0
    zipName = os.path.basename(zipPath)
    destPath = os.path.join(tempfile.gettempdir(), zipName)
    if not os.path.exists(destPath):
        os.mkdir(destPath)
    # extract all files
    with zipfile.ZipFile(zipPath) as zp:
        zp.extractall(destPath)

    # extract all the other zip files in the same directory
    for f in os.listdir(destPath):
        if f.endswith("zip"):
            zipCounter += 1
            zipPath = os.path.join(destPath, f)
            with zipfile.ZipFile(zipPath) as zp:
                zp.extractall(destPath)
            # delete zip file in the temp directory
            os.remove(zipPath)

