# file: JUnitHelper
# contains functions for compiling and running JUnit Tests

import os
import re
from subprocess import Popen, PIPE, STDOUT,TimeoutExpired
import configparser

import Loghelper

config = configparser.ConfigParser()
config.read("Simpelgrader.ini")
javaCPath = config["path"]["javaCompilerPath"]
javaPath = config["path"]["javaLauncherPath"]
jUnitPath = config["path"]["jUnitPath"]

'''
runs the JUnit-Tests inside the classname
'''
def runJUnitTest(filePath, className) -> bool:
    dirPath = os.path.dirname(filePath)
    classDir = os.path.dirname(filePath)
    javaArgs = f"-cp {jUnitPath}\*;{classDir} org.junit.runner.JUnitCore {className}"
    procContext = Popen(javaArgs, shell=True, env={"PATH": dirPath}, stdout=PIPE, stderr=STDOUT)
    procContext.wait()
    infoMessage = f"runJUnitTest: java exit code={procContext.returncode}"
    Loghelper.logInfo(infoMessage)
    return procContext.returncode == 0

'''
runs a single JUnit Test inside the classname
'''
def runJUnitTest(filePath, className, methodName) -> bool:
    return True

'''
Compiles a single java JUnit file
'''
def compileJavaTest(filePath) -> (int, str):
    dirPath = os.path.dirname(filePath)
    javaArgs = f"{javaCPath} -cp {jUnitPath}\*;.;{dirPath} {filePath}"
    infoMessage = f"compileJavaTest: java compiling {filePath}"
    Loghelper.logInfo(infoMessage)
    # shell=True?
    procContext = Popen(javaArgs, shell=True, env={"PATH": dirPath}, stdout=PIPE, stderr=STDOUT)
    procContext.wait()
    infoMessage = f"compileJavaTest: java exit code={procContext.returncode}"
    Loghelper.logInfo(infoMessage)
    javaCOutput = procContext.stdout.read()
    outputText = "OK"
    if len(javaCOutput) > 0:
        # cp1252 is import for Umlaute (utf8 does not work?)
        javaCOutput = javaCOutput.decode("cp1252")
        # Pattern to extract the error message only
        outputPattern = "java:\d+:\s+(.*)\r"
        if len(re.findall(outputPattern,javaCOutput)) > 0:
            outputText = re.findall(outputPattern,javaCOutput)[0]
        else:
            outputText = "Error"
    return (procContext.returncode, outputText)
