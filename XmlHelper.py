# file: XmlHelper.py
from os import path
from datetime import datetime
from lxml import etree as et

import Loghelper
from TaskAction import TaskAction
from TaskTest import TaskTest

nsmap =  {"sig": "urn:simpleGrader"}

class XmlHelper:

    '''
    Initialize the object
    '''
    def __init__(self, xmlFile):
        self.xmlPath = path.join(path.dirname(__file__), xmlFile)
        today = datetime.now().strftime("%d-%m-%Y")
        gradingReportName = f"GradingReport_{today}.xml"
        self.reportPath = path.join(path.dirname(__file__), gradingReportName)
        self.root = et.parse(self.xmlPath)

    '''
    Get all actions associated with this task and level
    '''
    def getActionList(self, taskName, taskLevel):
        xPathExpr = f".//sig:task[@name='{taskName}' and @level='{taskLevel}']/actions/action"
        actionElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        actionList = []
        for action in actionElements:
            ta = TaskAction(action.attrib["id"], action.attrib["active"], action.attrib["type"], action.text)
            actionList.append(ta)
        return actionList

    '''
    Get all tests associated with this task and level
    '''
    def getTestList(self, taskName, taskLevel):
        xPathExpr = f".//sig:task[@name='{taskName}' and @level='{taskLevel}']/tests/test"
        testElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        testList = []
        for test in testElements:
            testName = test.find("test-name").text
            tt = TaskTest(test.attrib["id"], testName, test.attrib["active"], test.find("test-type").text)
            tt.testDescription = test.find("test-description").text
            if test.find("test-type") == "JUNIT":
                tt.testMethod = test.find("test-method").text
            tt.testScore = test.find("test-score")
            testList.append(tt)
        return testList

    '''
    Generates a Xml file for all grading actions
    '''
    def generateGradingReport(self, actionList):
        root = et.Element("report")
        for action in actionList:
            gradeAction = et.SubElement(root, "gradeAction")
            actionType = et.SubElement(gradeAction, "type")
            actionType.text = action.type
            timeStamp = et.SubElement(gradeAction, "timestamp")
            timeStamp.text = datetime.strftime(action.timestamp, "%d.%m.%Y-%H:%M")
            gradeDescription = et.SubElement(gradeAction, "description")
            gradeDescription.text = action.description
            gradeStudent = et.SubElement(gradeAction, "student")
            gradeStudent.text = action.student
            gradeResult = et.SubElement(gradeAction, "gradeResult")
            gradeResult.text = str(action.result)
            gradeSucsess = et.SubElement(gradeAction, "gradeSuccess")
            gradeSucsess.text = str(action.success)

        # Write the report
        tree = et.ElementTree(root)
        tree.write(self.reportPath, pretty_print=True, xml_declaration=True, encoding="UTF-8")

        return self.reportPath

    def generateHtmlReport(self, xmlPath, semester, module, exercise):
        htmlPath = ""
        try:
            htmlPath = ".".join(xmlPath.split(".")[:-1])
            xsltPath = "GradingReport.xslt"
            xmlDom = et.parse(xmlPath)
            xsltDom = et.parse(xsltPath)
            transform = et.XSLT(xsltDom)
            newDom = transform(xmlDom, gradingTime=et.XSLT.strparam(datetime.now().strftime("%d.%m.%Y %H:%M")),
                                        semester=et.XSLT.strparam(semester),
                                        module=et.XSLT.strparam(module),
                                        exercise=et.XSLT.strparam(exercise))
            htmlText = et.tostring(newDom, pretty_print=True)
            # One more time tostring() returns bytes[] not str
            htmlLines = htmlText.decode().split("\n")
            with open(htmlPath, "w", encoding="utf-8") as fh:
                fh.writelines(htmlLines)
        except Exception as ex:
            infoMessage = f"XmlHelper->generateHtmlReport: Fehler {ex}"
            Loghelper.logError(infoMessage)
        return htmlPath
