# file: JavaHelper.py
import shutil
from subprocess import Popen, PIPE, STDOUT,TimeoutExpired
import configparser
import Loghelper
import os
import tempfile
import re

config = configparser.ConfigParser()
config.read("Simpleparser.ini")
javaCPath = config["path"]["javaCompilerPath"]
javaPath = config["path"]["javaLauncherPath"]

tempPath = os.path.join(tempfile.gettempdir(), "simplegrader")

'''
Compiles a single java file
old version
'''
def compileJava_Old(filePath):
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
        Loghelper.logInfo(infoMessage)
    filePath2 = os.path.join(studentIdPath, "app.java")
    shutil.copy(filePath, filePath2)
    javaArgs = f"{javaCPath} {filePath2}"
    # shell=True?
    procContext = Popen(javaArgs, shell=True, env = {"PATH": dirPath}, stdout=PIPE, stderr=STDOUT)
    procContext.wait()
    infoMessage = f"java exit code={procContext.returncode}"
    Loghelper.logInfo(infoMessage)
    # javaCOutput = procContext.stdout.read()
    return procContext.returncode

'''
Compiles a single java file
'''
def compileJava(filePath):
    dirPath = os.path.dirname(filePath)
    javaArgs = f"{javaCPath} {filePath}"
    infoMessage = f"Java compiling {filePath}"
    Loghelper.logInfo(infoMessage)
    # shell=True?
    procContext = Popen(javaArgs, shell=True, env = {"PATH": dirPath}, stdout=PIPE, stderr=STDOUT)
    procContext.wait()
    infoMessage = f"java exit code={procContext.returncode}"
    Loghelper.logInfo(infoMessage)
    javaCOutput = procContext.stdout.read()
    outputText = "OK"
    if len(javaCOutput) > 0:
        javaCOutput = javaCOutput.decode()
        # Pattern for error message
        outputPattern = "java:\d+:\s+(.*)\r"
        if len(re.findall(outputPattern,javaCOutput)) > 0:
            outputText = re.findall(outputPattern,javaCOutput)[0]
        else:
            outputText = "Error"

    return (procContext.returncode, outputText)

'''
Runs a class file
outputChecker is a lambda/function that does determine if the output is correct
'''
def runJava(filePath, outputChecker):
    dirPath = os.path.dirname(filePath)
    javaArgs = f"{javaPath} -cp {dirPath} {filePath}"
    infoMessage = f"Java compiling {filePath}"
    Loghelper.logInfo(infoMessage)
    outputText = "Leider nix"
    # shell=True?
    # Timeout for the java-Process
    timeOutSeconds = 15
    try:
        with Popen(javaArgs, shell=True, env={"PATH": dirPath},
                              stdout=PIPE, stderr=STDOUT,
                              encoding=None, errors=None) as proc:
            proc.wait(timeOutSeconds)
            outputText = proc.stdout.read()
            result = 0
            if outputChecker:
                result = outputChecker(outputText)
        return result
    except TimeoutExpired as ex:
        infoMessage = f"TimeOutExpired for Process {filePath}"
        Loghelper.logError(infoMessage)


'''
Extras:
>Running in a sandbox -> policy file
'''
