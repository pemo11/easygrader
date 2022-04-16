# file: CheckstyleHelper.py
'''
Später sollte alle Actions per Gradle ausgeführt werden - dann gibt es auch ein Reporting
'''
import os
import subprocess
import configparser
import tempfile
import Loghelper

config = configparser.ConfigParser()
config.read("Simpelgrader.ini")
javaCPath = config["path"]["checkstylePath"]
rulePath = config["path"]["checkstyleRulePath"]
checkstyleJarPath = config["path"]["checkstyJarPath"]

tempPath = os.path.join(tempfile.gettempdir(), "simpelgrader")

def runCheckstyle(javaPath):
    infoMessage = f"Checkstyle run with {javaPath}"
    Loghelper.logInfo(infoMessage)
    javarDir = os.path.dirname(javaPath)
    javaArgs = f"-cp {checkstyleJarPath} com.puppycrawl.tools.checkstyle.Main "
    javaArgs += f"-c {rulePath} {javaPath}"
    procContext = subprocess.Popen(javaArgs, shell=True, env = {"PATH": javaPath}, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    procContext.wait()
    infoMessage = f"Checkstyle exit-code={procContext.returncode}"
    Loghelper.logInfo(infoMessage)
    # javaCOutput = procContext.stdout.read()
    return procContext.returncode

