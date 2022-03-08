# file: ZipHelper.py
import os
import zipfile
import tempfile
import shutil
import Loghelper
import re

'''
Extract zip file in the temp directory
'''
def extractZip(destPath, zipPath):
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
        infoMessage = f"ZipHelper-> {tmpDirPath} created"
        Loghelper.logInfo(infoMessage)
    # extract all files
    with zipfile.ZipFile(zipPath) as zp:
        zp.extractall(destPath)

    infoMessage = f"ZipHelper-> {zipPath} extracted"
    Loghelper.logInfo(infoMessage)
    return tmpDirPath

    # extract all the other zip files in the same directory
    for f in os.listdir(tmpDirPath):
        if f.endswith("zip"):
            zipCounter += 1
            zipPath = os.path.join(destPath, f)
            with zipfile.ZipFile(zipPath) as zp:
                zp.extractall(destPath)
                infoMessage = f"ZipHelper-> {zipPath} extracted"
                Loghelper.logInfo(infoMessage)
            # delete zip file in the temp directory
            os.remove(zipPath)
            infoMessage = f"ZipHelper-> {zipPath} deleted"
            Loghelper.logInfo(infoMessage)

