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
checkstylePath = config["path"]["checkstylePath"]

tempPath = os.path.join(tempfile.gettempdir(), "simpelgrader")

'''
Runs a checkstyle check for a java file
'''
def runCheckstyle(javaPath) -> int:
    infoMessage = f"Checkstyle run with {javaPath}"
    Loghelper.logInfo(infoMessage)
    javarDir = os.path.dirname(javaPath)
    javaArgs = f"-cp {checkstylePath} com.puppycrawl.tools.checkstyle.Main "
    javaArgs += f"-c {rulePath} {javaPath}"
    procContext = subprocess.Popen(javaArgs, shell=True, env = {"PATH": javaPath}, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    procContext.wait()
    infoMessage = f"runCheckstyle: Checkstyle exit-code={procContext.returncode}"
    Loghelper.logInfo(infoMessage)
    # javaCOutput = procContext.stdout.read()
    return procContext.returncode

