# =============================================================================
# file: XmlHelper.py
# =============================================================================
import shutil
from os import path
from datetime import datetime
from lxml import etree as et
import os
import Loghelper
from TaskAction import TaskAction
from TaskTest import TaskTest

nsmap =  {"sig": "urn:simpelgrader"}

'''
Contains several functions for reading and writing xml files
'''
class XmlHelper:

    '''
    Initialize the object
    '''
    def __init__(self, xmlFile):
        currentDir = path.join(path.dirname(__file__))
        self.xmlPath = path.join(currentDir, xmlFile)
        self.root = et.parse(self.xmlPath)
        today = datetime.now().strftime("%d-%m-%Y")
        resultReportname = f"GradingResultreport_{today}.xml"
        # directory had been already created
        self.simpelgraderDir = os.path.join(os.path.expanduser("~"), "documents/simpelgrader")
        # copy all css files to the report directory
        XSLTDir = os.path.join(currentDir, "XSLT")
        for fi in [f for f in os.listdir(XSLTDir) if f.endswith("css")]:
            cssPath = os.path.join(XSLTDir, fi)
            shutil.copy(cssPath, self.simpelgraderDir)
        self.gradeResultReportpath = path.join(self.simpelgraderDir, resultReportname)
        actionReportName = f"GradingActionreport_{today}.xml"
        self.gradeActionReportpath = path.join(self.simpelgraderDir, actionReportName)
        submissionValidationReportname = f"SubmissionValidationreport_{today}.xml"
        self.submissionValidationReportpath = path.join(self.simpelgraderDir, submissionValidationReportname)
        feedbackReportName = f"GradingFeedbackReport_{today}.xml"
        self.feedbackReportpath = path.join(self.simpelgraderDir, feedbackReportName)

    '''
    tests if an exercise exists in the grading plan
    '''
    def exerciseExists(self, exercise) -> bool:
        xPathExpr = f".//sig:task[@name='{exercise}']"
        tasks = self.root.xpath(xPathExpr, namespaces=nsmap)
        return len(tasks) > 0

    '''
    Get all actions associated with this exercise
    '''
    def getActionList(self, exercise):
        # 20/04/22 - level ist jetzt Teil des Exercise-Namens, z.B. EA1A
        # xPathExpr = f".//sig:task[@name='{exercise}' and @level='{level}']/actions/action"
        xPathExpr = f".//sig:task[@name='{exercise}']/sig:actions/sig:action"
        actionElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        actionList = []
        for action in actionElements:
            ta = TaskAction(action.attrib["id"], action.attrib["active"], action.attrib["type"], action.findtext("sig:action-description", namespaces=nsmap))
            actionList.append(ta)
        return actionList

    '''
    Get the points associated with an exercise
    '''
    def getExercisePoints(self, exercise) -> int:
        xPathExpr = f".//sig:task[@name='{exercise}']"
        taskElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        if len(taskElements) > 0:
            points = int(taskElements[0].attrib["points"])
            return points
        else:
            return 0

    '''
    Get the points associated with an exercise and an action
    '''
    def getActionPoints(self, exercise, actionId) -> int:
        xPathExpr = f".//sig:task[@name='{exercise}']/sig:actions/sig:action[@id='{actionId}']"
        actionElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        if len(actionElements) > 0:
            points = actionElements[0].findtext("sig:action-points", namespaces=nsmap)
            return int(points) if points != "" else 0
        else:
            return 0

    '''
    Get the points associated with an exercise and a test
    '''
    def getTestPoints(self, exercise, testId) -> int:
        xPathExpr = f".//sig:task[@name='{exercise}']/sig:tests/sig:test[@id='{testId}']"
        testElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        if len(testElements) > 0:
            points = testElements[0].findtext("sig:test-points", namespaces=nsmap)
            return int(points) if points != "" else 0
        else:
            return 0

    '''
    Get all tests associated with this task/exercise
    '''
    def getTestList(self, exercise):
        xPathExpr = f".//sig:task[@name='{exercise}']/sig:tests/sig:test"
        testElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        testList = []
        for test in testElements:
            tt = TaskTest(test.attrib["id"], test.attrib["active"], test.find("sig:test-type", namespaces=nsmap).text)
            tt.testDescription = test.find("sig:test-description", namespaces=nsmap).text
            if test.find("sig:test-type", namespaces=nsmap).text.lower() == "junit":
                if test.find("sig:test-class", namespaces=nsmap) != None:
                    tt.testClass = test.find("sig:test-class", namespaces=nsmap).text
                else:
                    tt.testClass = ""
                if test.find("sig:test-method", namespaces=nsmap):
                    tt.testMethod = test.find("sig:test-method", namespaces=nsmap).text
                else:
                    tt.testMethod = ""
            tt.testScore = test.find("sig:test-score", namespaces=nsmap)
            testList.append(tt)
        return testList

    '''
    gets the textcompare test for the exercise
    '''
    def getTextCompareTest(self, exercise):
        xPathExpr = f".//sig:task[@name='{exercise}']/sig:tests/sig:test/sig:test-type[.='TextCompare']//parent::sig:test"
        testElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        if len(testElements) > 0:
            testElement = testElements[0]
            description = testElement.find("sig:test-description",namespaces={"sig": "urn:simpelgrader"}).text
            testClass = testElement.find("sig:test-testerClass",namespaces={"sig": "urn:simpelgrader"}).text
            testRegex = testElement.find("sig:test-testerRegex",namespaces={"sig": "urn:simpelgrader"}).text
            return {"description":description,"testClass":testClass,"testRegex":testRegex}
        else:
            return None

    '''
    Get all files associated with this task/exercise
    '''
    def getFileList(self, exercise):
        xPathExpr = f".//sig:task[@name='{exercise}']/sig:files/sig:file"
        fileElements = self.root.xpath(xPathExpr, namespaces=nsmap)
        fileList = [fi.text for fi in fileElements] # May be a filter if fi.endswith(".java") is needed
        return fileList

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
            xlActionType = et.SubElement(xlGradeAction, "type")
            xlActionType.text = gradeAction.type
            xlTimeStamp = et.SubElement(xlGradeAction, "timestamp")
            xlTimeStamp.text = datetime.strftime(gradeAction.timestamp, "%d.%m.%Y %H:%M")
            xlAction = et.SubElement(xlGradeAction, "action")
            xlAction.text = gradeAction.action
            xlFile =  et.SubElement(xlGradeAction, "file")
            xlFile.text = gradeAction.file
            # student id or better student name?
            xlStudentId = et.SubElement(xlGradeAction, "student")
            xlStudentId.text = str(gradeAction.submission.studentId)

        # Write the report
        tree = et.ElementTree(xlRoot)
        tree.write(self.gradeActionReportpath, pretty_print=True, xml_declaration=True, encoding="UTF-8")

        return self.gradeActionReportpath

    '''
    Generates an XML report from the list of feedback items
    '''
    def generateFeedbackReport(self, feedbackItemList):
        xlRoot = et.Element("report")
        for feedbackItem in feedbackItemList:
            xlFeedbackItem = et.SubElement(xlRoot, "feedbackItem")
            xlId = et.SubElement(xlFeedbackItem, "id")
            xlId.text = str(feedbackItem.submission.id)
            xlStudent = et.SubElement(xlFeedbackItem, "student")
            xlStudent.text = str(feedbackItem.submission.studentId)
            xlExercise = et.SubElement(xlFeedbackItem, "exercise")
            xlExercise.text = feedbackItem.submission.exercise
            xlTimeStamp = et.SubElement(xlFeedbackItem, "timestamp")
            xlTimeStamp.text = datetime.strftime(feedbackItem.submission.timestamp, "%d.%m.%Y %H:%M")
            xlMessage = et.SubElement(xlFeedbackItem, "message")
            xlMessage.text = feedbackItem.message
            xlSeverity = et.SubElement(xlFeedbackItem, "severity")
            xlSeverity.text = feedbackItem.severity
            xlCheckstyleReportpath = et.SubElement(xlFeedbackItem, "checkstyleReportpath")
            xlCheckstyleReportpath.text = feedbackItem.checkstyleReportpath
            xlJunitReportpath = et.SubElement(xlFeedbackItem, "jUnitReportpath")
            xlJunitReportpath.text = feedbackItem.jUnitReportpath
            xlTextcompareReportpath = et.SubElement(xlFeedbackItem, "textCompareReportpath")
            xlTextcompareReportpath.text = feedbackItem.textCompareReportpath
            xlSubmissionReportpath = et.SubElement(xlFeedbackItem, "submissionReportpath")
            xlSubmissionReportpath.text = feedbackItem.submissionReportpath

        # Write the report
        tree = et.ElementTree(xlRoot)
        tree.write(self.feedbackReportpath, pretty_print=True, xml_declaration=True, encoding="UTF-8")

        return self.feedbackReportpath

    '''
    Generates XML/HTML reports for each submission feedback
    '''
    def generateSubmissionFeedbackReports(self, feedbackDic) -> {}:
        reportDic = {}
        for studentId in feedbackDic:
            for submissionFeedback in feedbackDic[studentId]:
                infoMessage = f"generateSubmissionFeedbackReports: generating feedback report for Student/Exercise {submissionFeedback.studentId}/{submissionFeedback.exercise}"
                Loghelper.logInfo(infoMessage)
                xlReport = et.Element("report")
                xlStudent = et.SubElement(xlReport, "student")
                xlStudent.text = str(submissionFeedback.studentId)
                xlExercise = et.SubElement(xlReport, "exercise")
                xlExercise.text = submissionFeedback.exercise
                xlTestCount = et.SubElement(xlReport, "testCount")
                xlTestCount.text = str(submissionFeedback.testCount)
                xlExercisePoints = et.SubElement(xlReport, "exercisePoints")
                xlExercisePoints.text = str(submissionFeedback.exercisePoints)
                xlTotalPoints = et.SubElement(xlReport, "totalPoints")
                xlTotalPoints.text = str(submissionFeedback.totalPoints)
                xlActionSummary = et.SubElement(xlReport, "actionSummary")
                xlActionSummary.text = submissionFeedback.actionSummary
                xlTestSummary = et.SubElement(xlReport, "testSummary")
                xlTestSummary.text = submissionFeedback.testSummary
                xlFeedbackSummary = et.SubElement(xlReport, "feedbackSummary")
                xlFeedbackSummary.text = submissionFeedback.feedbackSummary
                # TODO: student name instead of id
                submissionFeedbackReportpath = os.path.join(self.simpelgraderDir, f"{studentId}_{submissionFeedback.exercise}_submissionFeedback.xml")
                # Write the report
                tree = et.ElementTree(xlReport)
                tree.write(submissionFeedbackReportpath, pretty_print=True, xml_declaration=True, encoding="UTF-8")
                # TODO: Convert to html

                # save the reportpath in the dictionary with the studenId as key
                if reportDic.get(studentId) == None:
                    reportDic[studentId] = submissionFeedbackReportpath

        return reportDic


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
    Generates a single submission report for all submission feedback and return the html path
    '''
    def generateSubmissionReport(self, feedbackDic) -> str:
        # TODO: do some coding...
        infoMessage = f"generateSubmissionReport: generating feedback report for {len(feedbackDic)} submissions"
        Loghelper.logInfo(infoMessage)
        xlReport = et.Element("report")
        for studentId in feedbackDic:
            for submissionFeedback in feedbackDic[studentId]:
                xlSubmission = et.SubElement(xlReport, "submission")
                xlStudent = et.SubElement(xlSubmission, "student")
                xlStudent.text = str(submissionFeedback.studentId)
                xlExercise = et.SubElement(xlSubmission, "exercise")
                xlExercise.text = submissionFeedback.exercise
                xlActionCount = et.SubElement(xlSubmission, "actionCount")
                xlActionCount.text = str(submissionFeedback.actionCount)
                xlTestCount = et.SubElement(xlSubmission, "testCount")
                xlTestCount.text = str(submissionFeedback.testCount)
                xlExercisePoints = et.SubElement(xlSubmission, "exercisePoints")
                xlExercisePoints.text = str(submissionFeedback.exercisePoints)
                xlTotalPoints = et.SubElement(xlSubmission, "totalPoints")
                xlTotalPoints.text = str(submissionFeedback.totalPoints)
                xlActionSummary = et.SubElement(xlSubmission, "actionSummary")
                xlActionSummary.text = submissionFeedback.actionSummary
                xlTestSummary = et.SubElement(xlReport, "testSummary")
                xlTestSummary.text = submissionFeedback.testSummary
                xlFeedbackSummary = et.SubElement(xlSubmission, "feedbackSummary")
                xlFeedbackSummary.text = submissionFeedback.feedbackSummary

        # submission report path in the report directory contains the current date
        heute = datetime.now().date()
        submissionPath = os.path.join(self.simpelgraderDir, f"SubmissionReport_{heute}.xml")
        # Write the report
        tree = et.ElementTree(xlReport)
        tree.write(submissionPath, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        # convert xml to html
        htmlPath = self.convertSubmissionReport2Html(submissionPath)
        return htmlPath


    '''
    Converts a grading result xml report into html
    '''
    def convertGradingResultReport2Html(self, xmlPath, semester, module, exercise):
        htmlPath = ""
        try:
            htmlPath = ".".join(xmlPath.split(".")[:-1]) + ".html"
            xsltPath = "XSLT/GradingResultreport.xslt"
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
            infoMessage = f"convertGradingResultReport2Html: generated {htmlPath}"
            Loghelper.logInfo(infoMessage)
        except Exception as ex:
            infoMessage = f"convertGradingResultReport2Html: error ({ex})"
            Loghelper.logError(infoMessage)
        return htmlPath

    '''
    Converts a feedback xml report into html
    '''
    def convertFeedbackReport2Html(self, xmlPath, semester, module, exercise):
        htmlPath = ""
        try:
            htmlPath = ".".join(xmlPath.split(".")[:-1]) + ".html"
            xsltPath = "XSLT/FeedbackReport.xslt"
            xmlDom = et.parse(xmlPath)
            xsltDom = et.parse(xsltPath)
            transform = et.XSLT(xsltDom)
            newDom = transform(xmlDom, feedbackTime=et.XSLT.strparam(datetime.now().strftime("%d.%m.%Y %H:%M")),
                               semester=et.XSLT.strparam(semester),
                               module=et.XSLT.strparam(module),
                               exercise=et.XSLT.strparam(exercise))
            htmlText = et.tostring(newDom, pretty_print=True)
            # One more time tostring() returns bytes[] not str
            htmlLines = htmlText.decode().split("\n")
            with open(htmlPath, "w", encoding="utf-8") as fh:
                fh.writelines(htmlLines)
            infoMessage = f"convertFeedbackReport2Html: generated {htmlPath}"
            Loghelper.logInfo(infoMessage)
        except Exception as ex:
            infoMessage = f"convertFeedbackReport2Html: error ({ex})"
            Loghelper.logError(infoMessage)
        return htmlPath

    '''
    Converts a submission validation xml report into html
    '''
    def convertSubmissionValidationReport2Html(self, xmlPath) -> str:
        htmlPath = ""
        try:
            htmlPath = ".".join(xmlPath.split(".")[:-1]) + ".html"
            xsltPath = "XSLT/SubmissionValidationReport.xslt"
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

    '''
    Converts a checkstyle xml report into html
    '''
    def convertCheckstyleReport2Html(self, xmlPath, student, exercise) -> str:
        htmlPath = ""
        try:
            htmlPath = ".".join(xmlPath.split(".")[:-1]) + ".html"
            xsltPath = "XSLT/CheckstyleReport.xslt"
            xmlDom = et.parse(xmlPath)
            xsltDom = et.parse(xsltPath)
            transform = et.XSLT(xsltDom)
            newDom = transform(xmlDom, student=et.XSLT.strparam(student),
                                        exercise=et.XSLT.strparam(exercise))
            htmlText = et.tostring(newDom, pretty_print=True)
            # One more time tostring() returns bytes[] not str
            htmlLines = htmlText.decode().split("\n")
            with open(htmlPath, "w", encoding="utf-8") as fh:
                fh.writelines(htmlLines)
            infoMessage = f"convertCheckstyleReport2Html: generated {htmlPath}"
            Loghelper.logInfo(infoMessage)
        except Exception as ex:
            infoMessage = f"convertCheckstyleReport2Html: error ({ex})"
            Loghelper.logError(infoMessage)
        return htmlPath

    '''
    Converts a JUnit xml report into html
    '''
    def convertJUnitReport2Html(self, xmlPath, student, exercise) -> str:
        htmlPath = ""
        try:
            htmlPath = ".".join(xmlPath.split(".")[:-1]) + ".html"
            xsltPath = "XSLT/JUnitReport.xslt"
            xmlDom = et.parse(xmlPath)
            xsltDom = et.parse(xsltPath)
            transform = et.XSLT(xsltDom)
            newDom = transform(xmlDom, student=et.XSLT.strparam(student),
                                        exercise=et.XSLT.strparam(exercise))
            htmlText = et.tostring(newDom, pretty_print=True)
            # One more time tostring() returns bytes[] not str
            htmlLines = htmlText.decode().split("\n")
            with open(htmlPath, "w", encoding="utf-8") as fh:
                fh.writelines(htmlLines)
            infoMessage = f"convertJUnitReport2Html: generated {htmlPath}"
            Loghelper.logInfo(infoMessage)
        except Exception as ex:
            infoMessage = f"convertJUnitReport2Html: error ({ex})"
            Loghelper.logError(infoMessage)
        return htmlPath

    '''
    Converts a submission xml report to html
    '''
    def convertSubmissionReport2Html(self, xmlPath) -> str:
        htmlPath = ""
        try:
            htmlPath = ".".join(xmlPath.split(".")[:-1]) + ".html"
            xsltPath = "XSLT/SubmissionReport.xslt"
            xmlDom = et.parse(xmlPath)
            xsltDom = et.parse(xsltPath)
            transform = et.XSLT(xsltDom)
            newDom = transform(xmlDom)
            htmlText = et.tostring(newDom, pretty_print=True)
            # One more time tostring() returns bytes[] not str
            htmlLines = htmlText.decode().split("\n")
            with open(htmlPath, "w", encoding="utf-8") as fh:
                fh.writelines(htmlLines)
            infoMessage = f"convertSubmissionReport2Html: generated {htmlPath}"
            Loghelper.logInfo(infoMessage)
        except Exception as ex:
            infoMessage = f"convertSubmissionReport2Html: error ({ex})"
            Loghelper.logError(infoMessage)
        return htmlPath
