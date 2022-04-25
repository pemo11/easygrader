# file: XmlHelper.py
from os import path
from datetime import datetime
from lxml import etree as et

import Loghelper
from TaskAction import TaskAction
from TaskTest import TaskTest

nsmap =  {"sig": "urn:simpelgrader"}

class XmlHelper:

    '''
    Initialize the object
    '''
    def __init__(self, xmlFile):
        self.xmlPath = path.join(path.dirname(__file__), xmlFile)
        today = datetime.now().strftime("%d-%m-%Y")
        resultReportname = f"GradingResultReport_{today}.xml"
        self.gradeResultReportpath = path.join(path.dirname(__file__), resultReportname)
        actionReportName = f"GradingActionReport_{today}.xml"
        self.gradeActionReportpath = path.join(path.dirname(__file__), actionReportName)
        submissionValidationReportname = f"SubmissionValidationReport_{today}.xml"
        self.submissionValidationReportpath = path.join(path.dirname(__file__), submissionValidationReportname)
        self.root = et.parse(self.xmlPath)

    '''
    tests if an exercise exists in the grading plan
    '''
    def exerciseExists(self, exercise) -> bool:
        xPathExpr = f".//sig:task[@exercise='{exercise}']"
        exercise = self.root.xpath(xPathExpr, namespaces=nsmap)
        return len(exercise) > 0

    '''
    Get all actions associated with this exercise
    '''
    def getActionList(self, exercise):
        # 20/04/22 - level ist jetzt Teil des Exercise-Namens, z.B. EA1A
        # xPathExpr = f".//sig:task[@name='{exercise}' and @level='{level}']/actions/action"
        xPathExpr = f".//sig:task[@exercise='{exercise}']/sig:actions/sig:action"
        actionElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        actionList = []
        for action in actionElements:
            ta = TaskAction(action.attrib["id"], action.attrib["active"], action.attrib["type"], action.text)
            actionList.append(ta)
        return actionList

    '''
    Get all tests associated with this task/exercise
    '''
    def getTestList(self, exercise):
        xPathExpr = f".//sig:task[@exercise='{exercise}']/sig:tests/sig:test"
        testElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        testList = []
        for test in testElements:
            tt = TaskTest(test.attrib["id"], test.attrib["active"], test.find("sig:test-type", namespaces=nsmap).text)
            tt.testDescription = test.find("sig:test-description", namespaces=nsmap).text
            if test.find("sig:test-type", namespaces=nsmap) == "JUNIT":
                tt.testMethod = test.find("sig:test-method", namespaces=nsmap).text
            tt.testScore = test.find("sig:test-score", namespaces=nsmap)
            testList.append(tt)
        return testList

    '''
    Get all files associated with this task/exercise
    '''
    def getFileList(self, exercise):
        xPathExpr = f".//sig:task[@exercise='{exercise}']/sig:files/sig:file"
        fileElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        fileList = [fi.text for fi in fileElements] # May be a filter if fi.endswith(".java") is needed
        return fileList

    '''
    Generates a Xml file for all grading results
    '''
    def generateGradingResultReport(self, resultList):
        root = et.Element("report")
        for gradeResult in resultList:
            xlGradeResult = et.SubElement(root, "gradeResult")
            resultType = et.SubElement(xlGradeResult, "type")
            resultType.text = gradeResult.type
            timeStamp = et.SubElement(xlGradeResult, "timestamp")
            timeStamp.text = datetime.strftime(gradeResult.timestamp, "%d.%m.%Y %H:%M")
            gradeDescription = et.SubElement(xlGradeResult, "description")
            gradeDescription.text = gradeResult.description
            gradeStudent = et.SubElement(xlGradeResult, "student")
            # TODO: Should be name not id
            gradeStudent.text = str(gradeResult.submission.studentId)
            gradePoints = et.SubElement(xlGradeResult, "points")
            gradePoints.text = str(gradeResult.points)
            gradeErrorMessage  = et.SubElement(xlGradeResult, "message")
            gradeErrorMessage.text = gradeResult.errorMessage
            gradeSuccess = et.SubElement(xlGradeResult, "gradeSuccess")
            gradeSuccess.text = str(gradeResult.success)

        # Write the report
        tree = et.ElementTree(root)
        tree.write(self.gradeResultReportpath, pretty_print=True, xml_declaration=True, encoding="UTF-8")

        return self.gradeResultReportpath

    '''
    Generates an XML report from the list of grade actions
    '''
    def generateGradingActionReport(self, actionList):
        xlRoot = et.Element("report")
        for gradeAction in actionList:
            xlGradeAction = et.SubElement(xlRoot, "gradeAction")
            actionType = et.SubElement(xlGradeAction, "type")
            actionType.text = gradeAction.type
            timeStamp = et.SubElement(xlGradeAction, "timestamp")
            timeStamp.text = datetime.strftime(gradeAction.timestamp, "%d.%m.%Y %H:%M")
            action = et.SubElement(xlGradeAction, "action")
            action.text = gradeAction.action
            # student id or student name?
            studentId = et.SubElement(xlGradeAction, "student")
            studentId.text = str(gradeAction.submission.studentId)

        # Write the report
        tree = et.ElementTree(xlRoot)
        tree.write(self.gradeActionReportpath, pretty_print=True, xml_declaration=True, encoding="UTF-8")

        return self.gradeActionReportpath

    '''
    Converts a grading xml report into html
    '''
    def convertGradingReport2Html(self, xmlPath, semester, module, exercise):
        htmlPath = ""
        try:
            htmlPath = ".".join(xmlPath.split(".")[:-1]) + ".html"
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
            infoMessage = f"convertGradingReport2Html: generated {htmlPath}"
            Loghelper.logInfo(infoMessage)
        except Exception as ex:
            infoMessage = f"convertGradingReport2Html: error ({ex})"
            Loghelper.logError(infoMessage)
        return htmlPath

    '''
    Validates the current gradingplan file against the xsd schema
    '''
    def validateXml(self) -> bool:
        try:
            xsdPath = path.join(path.dirname(__file__), "gradingplan.xsd")
            if not path.exists(xsdPath):
                return False
            xmlSchemaDoc = et.parse(xsdPath)
            xmlSchema = et.XMLSchema(xmlSchemaDoc)
            xmlDoc = et.parse(self.xmlPath)
            result = xmlSchema.validate(xmlDoc)
        except Exception as ex:
            Loghelper.logError(f"validateXml: Fehler bei der Xml-Validierung ({ex})")
            result = False
        return result

    '''
    Generates a Xml file for all submission validation entries
    '''
    def generateSubmissionValidationReport(self, submissionValidationList) -> str:
        root = et.Element("report")
        for submissionEntry in submissionValidationList:
            subValidation = et.SubElement(root, "submissionValidation")
            submissionId = et.SubElement(subValidation, "submissionId")
            submissionId.text = str(submissionEntry.submissionId)
            studentId = et.SubElement(subValidation, "studentId")
            studentId.text = str(submissionEntry.studentId)
            exercise = et.SubElement(subValidation, "exercise")
            exercise.text = submissionEntry.exercise
            validationType = et.SubElement(subValidation, "type")
            validationType.text = submissionEntry.type
            validationMessage = et.SubElement(subValidation, "message")
            validationMessage.text = submissionEntry.message
            timeStamp = et.SubElement(subValidation, "timestamp")
            timeStamp.text = datetime.strftime(submissionEntry.timestamp, "%d.%m.%Y %H:%M")

        # Write the report
        tree = et.ElementTree(root)
        tree.write(self.submissionValidationReportpath, pretty_print=True, xml_declaration=True, encoding="UTF-8")

        return self.submissionValidationReportpath

    '''
    Converts a submission validation xml report into html
    '''
    def convertSubmissionValidationReport2Html(self, xmlPath) -> str:
        htmlPath = ""
        try:
            htmlPath = ".".join(xmlPath.split(".")[:-1]) + ".html"
            xsltPath = "SubmissionValidationReport.xslt"
            xmlDom = et.parse(xmlPath)
            xsltDom = et.parse(xsltPath)
            transform = et.XSLT(xsltDom)
            newDom = transform(xmlDom, gradingTime=et.XSLT.strparam(datetime.now().strftime("%d.%m.%Y %H:%M")))
            htmlText = et.tostring(newDom, pretty_print=True)
            # One more time tostring() returns bytes[] not str
            htmlLines = htmlText.decode().split("\n")
            with open(htmlPath, "w", encoding="utf-8") as fh:
                # important: writelines does not add a \n from the beginning
                fh.writelines(line + "\n" for line in htmlLines)
            infoMessage = f"convertValidationReport2Html: generated {htmlPath}"
            Loghelper.logInfo(infoMessage)
        except Exception as ex:
            infoMessage = f"convertValidationReport2Html: error ({ex})"
            Loghelper.logError(infoMessage)
        return htmlPath
