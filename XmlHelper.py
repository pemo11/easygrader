# file: XmlHelper.py
from os import path
from datetime import datetime
from lxml import etree as et
from TaskAction import TaskAction
from TaskTest import TaskTest

nsmap =  {"eag": "urn:simpleGrader"}

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
        xPathExpr = f".//eag:task[@name='{taskName}' and @level='{taskLevel}']/actions/action"
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
        xPathExpr = f".//eag:task[@name='{taskName}' and @level='{taskLevel}']/tests/test"
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
    Erzeugt eine Xml-Datei für alle Grading Actions
    '''
    def generateGradingReport(self, actionList):
        root = et.Element("report")
        for action in actionList:
            gradeAction = et.SubElement(root, "gradeAction")
            timeStamp = et.SubElement(gradeAction, "timestamp")
            timeStamp.text = datetime.strftime(action.timestamp, "%d.%m.%Y-%H:%M")
            gradeDescription = et.SubElement(gradeAction, "description")
            gradeDescription.text = action.description
            gradeSubmission = et.SubElement(gradeAction, "submission")
            gradeSubmission.text = action.submission
            gradeResult = et.SubElement(gradeAction, "gradeResult")
            gradeResult.text = action.result

        # Write the report
        tree = et.ElementTree(root)
        tree.write(self.reportPath, pretty_print=True, xml_declaration=True, encoding="UTF-8")
