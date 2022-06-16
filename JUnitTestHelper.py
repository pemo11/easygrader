# =============================================================================
# file: JUnitHelper
# contains functions for compiling and running JUnit Tests
# =============================================================================
import os
import re
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import configparser
from lxml import etree as et

import Loghelper

class JUnitHelper:

    def __init__(self, configPath):
        # read the paths from the in file
        config = configparser.ConfigParser()
        config.read(configPath)
        self.javaPath = config["path"]["javaLauncherPath"]
        self.javaCPath = config["path"]["javaCompilerPath"]
        self.jUnitPath = config["path"]["jUnitPath"]
        self.solutionPath = config["path"]["solutionPath"]

    '''
    Runs the JUnit-Tests inside the classname
    class file should already exists
    '''
    def runJUnitTest(self, exercise, testClass) -> ():
        dirPath = os.path.join(self.solutionPath, exercise)
        classPath = os.path.join(dirPath, testClass + ".class")
        if not os.path.exists(classPath):
            infoMessage = f"runJUnitTest: {classPath} class not found"
            Loghelper.logWarning(infoMessage)
            return (-1, infoMessage)
        javaArgs = f"{self.javaPath} -cp {self.jUnitPath}\*;.;{dirPath} org.junit.runner.JUnitCore {testClass}"
        procContext = Popen(javaArgs, shell=True, env={"PATH": dirPath}, stdout=PIPE, stderr=STDOUT)
        procContext.wait()
        retCode = procContext.returncode
        infoMessage = f"runJUnitTest: java exit code={retCode}"
        Loghelper.logInfo(infoMessage)
        javaCOutput = procContext.stdout.read()
        javaCOutput = javaCOutput.decode("cp1252")
        # if test ran sucessfully then convert JUnit text output to simple xml
        if retCode == 0:
            jUnitXml = self.createJUnitXml(javaCOutput)
        else:
            jUnitXml = ""
        return (retCode, jUnitXml)

    '''
    Runs a single JUnit test method inside the classname
    '''
    def runJUnitTestMethod(self, filePath, className, methodName) -> bool:
        # not needed at the moment and needs a custom java class anyway
        return True

    '''
    Compiles a single java JUnit file
    '''
    def compileJavaTest(self, filePath) -> (int, str):
        dirPath = os.path.dirname(filePath)
        javaArgs = f"{self.javaCPath} -cp {self.jUnitPath}\*;.;{dirPath} {filePath}"
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
            # Should not be necessary - the console output does contains the wrong encoding
            # maybe utf8/win1252 issue?
            # https://utf8-chartable.de/unicode-utf8-table.pl?utf8=char
            javaCOuput = javaCOutput.replace("Ã¼", "ü")

            # Pattern to extract the error message only
            outputPattern = "java:\d+:\s+(.*)\r"
            if len(re.findall(outputPattern,javaCOutput)) > 0:
                outputText = re.findall(outputPattern,javaCOutput)[0]
            else:
                outputText = "Error"
        return (procContext.returncode, outputText)

    '''
    Converts JUnit output to xml
    '''
    def createJUnitXml(self, jUnitOutput) -> str:
        # several regex patterns for the JUnit output
        pattern1 = r"JUnit\s+version\s+([0-9.]+)"
        pattern2 = r"Time:\s+([0-9,]+)"
        pattern3 = r"OK\s+\((\d+)\s+test"
        pattern4 = r"There\s+(\bwas\b|\bwere\b)\s+(\d+)\s+(\bfailure\b|\bfailures\b)"
        pattern5 = r"(\d+)\)\s+(\w+)\((\w+)\)"
        errorMode = False
        testMode = False
        testId = 0

        # create the root element
        xlRoot = et.Element("junitTest")

        # walk the lines
        for line in jUnitOutput.split("\n"):
            # create only one test element
            if testMode == False:
                testMode = True
                testId += 1
                xlTest = et.SubElement(xlRoot, "test")
                xlTest.attrib["id"] = f"{testId:03d}"
                xlResult = et.SubElement(xlTest, "result")
            # match the first line
            if re.match(pattern1, line):
                version = re.match(pattern1, line)[1]
                xlRoot.attrib["version"] = version
            # match the second line
            if re.match(pattern2, line):
                rTime = re.match(pattern2, line)[1]
            # match the summary line if all tests are OK
            if re.match(pattern3, line):
                testCount = re.match(pattern3, line)[1]
                xlResult.text = "OK"
                xlResult.attrib["testCount"] = testCount
            # match the summary line if they are errors
            if re.match(pattern4, line):
                errorCount = re.search(pattern4, line)[2]
                xlResult.text = "Error"
                xlErrors = et.SubElement(xlTest, "errors")
                errorMode = True
            # match the line with the error details
            if errorMode and re.match(pattern5, line):
                elements = re.search(pattern5, line)
                nr = elements[1]
                testMethod = elements[2]
                testClass = elements[3]
                xlError = et.SubElement(xlErrors, "error")
                # set the id attribute
                xlError.attrib["id"] = nr
                xlMethod = et.SubElement(xlError, "method")
                xlMethod.text = testMethod
                xlClass = et.SubElement(xlError, "class")
                xlClass.text = testClass

        # return a nice xml string - decode() to make it a str, cp1252 is for the Umlaute
        return et.tostring(xlRoot, pretty_print=True).decode("cp1252")

    '''
    gets the return value from the JUnit xml
    '''
    def getJUnitResult(self, xmlText) -> str:
        xlRoot = et.fromstring(xmlText)
        xPathExpr = f".//result"
        resultElements = xlRoot.xpath(xPathExpr)
        if len(resultElements) > 0:
            return resultElements[0].text
        else:
            return ""

