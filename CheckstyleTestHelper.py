# =============================================================================
# file: CheckstyleTestHelper.py
# =============================================================================

'''
Später sollte alle Actions per Gradle ausgeführt werden - dann gibt es auch ein Reporting
'''
import os
import subprocess
import configparser
import tempfile
import Loghelper

class CheckstyleTestHelper:

    def __init__(self, configPath):
        # get the import programm pathes from the ini file
        config = configparser.ConfigParser()
        config.read(configPath)
        javaLPath = config["path"]["javaLauncherPath"]
        checkstylePath = config["path"]["checkstylePath"]
        rulePath = config["path"]["checkstyleRulePath"]

    # get the temp directory for the application
    tempPath = os.path.join(tempfile.gettempdir(), "simpelgrader")

    '''
    Runs a checkstyle check for a java file
    '''
    def runCheckstyle(self, javaPath) -> int:
        infoMessage = f"Checkstyle run with {javaPath}"
        Loghelper.logInfo(infoMessage)
        javarDir = os.path.dirname(self.javaPath)
        javaArgs = f"{self.javaLPath} -cp {self.checkstylePath} com.puppycrawl.tools.checkstyle.Main "
        javaArgs += f"-c {self.rulePath} -f xml {self.javaPath}"
         # Timeout for the java-Process
        timeOutSeconds = 5
        try:
            procContext = subprocess.Popen(javaArgs, shell=True, env = {"PATH": javarDir}, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            procContext.wait(timeOutSeconds)
            exitCode = procContext.returncode
            infoMessage = f"runCheckstyle: Checkstyle exit-code={procContext.returncode}"
            Loghelper.logInfo(infoMessage)
            checkstyleOutput = procContext.stdout.read()
            if len(checkstyleOutput) > 0:
                checkstyleOutput = checkstyleOutput.decode("cp1252")
        except subprocess.TimeoutExpired as ex:
            infoMessage = f"runCheckstyle: Timeout error"
            Loghelper.logError(infoMessage)
            exitCode = -1
            checkstyleOutput = "Checkstyle Timeout"

        # the return text is xml with a checkstyle root and many error elements
        return (exitCode, checkstyleOutput)

