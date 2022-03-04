# file: JavaHelper.py
import shutil
import subprocess
import configparser
import loghelper
import os
import tempfile
import re

config = configparser.ConfigParser()
config.read("simpleparser.ini")
javaPath = config["path"]["javaPath"]

tempPath = os.path.join(tempfile.gettempdir(), "simplegrader")

'''
Compiles a single java file
'''
def compileJava(filePath):
    dirPath = os.path.dirname(filePath)
    fileName = os.path.basename(filePath)
    # Copy java file to tmp dir
    pattern = "(\d+)_App.java"
    studentId = re.findall(pattern, fileName)[0]
    # Create temp directory for studentId
    studentIdPath = os.path.join(tempPath, studentId)
    if not os.path.exists(studentIdPath):
        os.mkdir(studentIdPath)
        infoMessage = f"Created directory {studentIdPath}"
        loghelper.logInfo(infoMessage)
    filePath2 = os.path.join(studentIdPath, "app.java")
    shutil.copy(filePath, filePath2)
    javaArgs = f"{javaPath} {filePath2}"
    # shell=True?
    procContext = subprocess.Popen(javaArgs, shell=True, env = {"PATH": dirPath}, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    procContext.wait()
    infoMessage = f"Exit-Code={procContext.returncode}"
    loghelper.logInfo(infoMessage)
    # javaCOutput = procContext.stdout.read()
    return procContext.returncode
