<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    version="1.0">
    <xsl:param name="gradingTime"/>
    <xsl:template match="/">
        <html>
             <head>
                <meta charset="UTF-8" />
                <link href="Simpelgrader.css" type="text/css" rel="stylesheet" />
            </head>
           <body>
                <h3>Submission-Report <xsl:value-of select="$gradingTime"/> </h3>
                <xsl:for-each select="//submission">
                    <table id="infoTable">
                        <tr><td class="info">Nr</td><td><xsl:value-of select="position()"/></td></tr>
                        <tr><td class="info1">Student</td><td class="info2"><xsl:value-of select="student"/> (<xsl:value-of select="studentId"/>)</td></tr>
                        <tr><td>Exercise</td><td><xsl:value-of select="exercise"/></td></tr>
                        <tr><td>Number of actions</td><td><xsl:value-of select="actionCount"/></td></tr>
                        <tr><td>Number of tests</td><td><xsl:value-of select="testCount"/></td></tr>
                        <tr><td>Exercise points</td><td><xsl:value-of select="exercisePoints"/></td></tr>
                        <tr><td>Total points</td><td><xsl:value-of select="totalPoints"/></td></tr>
                        <tr><td>Action summary</td><td><xsl:value-of select="actionSummary"/></td></tr>
                        <tr><td>Test summary</td><td><xsl:value-of select="testSummary"/></td></tr>
                        <tr><td>Checkstyle result</td>
                            <td>
                               <xls:element name="a">
                                    <xsl:attribute name="href">file:///<xsl:value-of select="submissionReportpath" /></xsl:attribute>
                                    <xsl:value-of select="studentId"/>
                               </xls:element>
                            </td>
                        </tr>
                        <tr><td>Text-Compare result</td>
                            <td>
                               <xls:element name="a">
                                    <xsl:attribute name="href">file:///<xsl:value-of select="submissionReportpath" /></xsl:attribute>
                                    <xsl:value-of select="studentId"/>
                               </xls:element>
                            </td>
                        </tr>
                        <tr><td>JUnit result</td>
                            <td>
                               <xls:element name="a">
                                    <xsl:attribute name="href">file:///<xsl:value-of select="submissionReportpath" /></xsl:attribute>
                                    <xsl:value-of select="studentId"/>
                               </xls:element>
                            </td>
                        </tr>
                        <tr><td>Feedback summary</td><td><xsl:value-of select="feedbackSummary"/></td></tr>
                    </table>
                    <hr/>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
