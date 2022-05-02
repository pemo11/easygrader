<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:xs="http://www.w3.org/2001/XMLSchema"
        version="1.0" xmlns:xls="http://www.w3.org/1999/XSL/Transform">
    <xsl:param name="semester"/>
    <xsl:param name="module"/>
    <xsl:param name="exercise"/>
    <xsl:param name="feedbackTime"/>
    <xsl:template match="/">
        <html>
             <head>
                <meta charset="UTF-8" />
                <link href="GradingResultReport.css" type="text/css" rel="stylesheet" />
            </head>
           <body>
                <h3>Feedback-Report <xsl:value-of select="$feedbackTime"/> - <xsl:value-of select="$module"/>/<xsl:value-of select="$exercise"/> (<xsl:value-of select="$semester"/>)</h3>
                <table id="entries">
                    <tr bgcolor="#9acd32">
                        <th>Timestamp</th>
                        <th>Student</th>
                        <th>Exercise</th>
                        <th>Message</th>
                        <th>Severity</th>
                        <th>Checkstyle-Report</th>
                        <th>JUnit-Report</th>
                    </tr>
                    <xsl:for-each select="//feedbackItem">
                        <tr>
                            <td><xsl:value-of select="timestamp"/></td>
                            <td><xsl:value-of select="student"/></td>
                            <td><xsl:value-of select="exercise"/></td>
                            <td><xsl:value-of select="message"/></td>
                            <xsl:choose>
                                <xsl:when test="severity = 'High'">
                                    <td style="background-color:orange"><xsl:value-of select="severity"/></td>
                                </xsl:when>
                                <xsl:otherwise>
                                    <td bgcolor='lightgrey'><xsl:value-of select="severity"/></td>
                                </xsl:otherwise>
                            </xsl:choose>
                            <td>
                                <xls:element name="a">
                                    <xsl:attribute name="href">
                                        file:///<xsl:value-of select="checkstyleReportpath" />
                                    </xsl:attribute>
                                    <xsl:text>Checkstyle-Report</xsl:text>
                                </xls:element>
                            </td>
                            <td>
                                <xls:element name="a">
                                    <xsl:attribute name="href">
                                        file:///<xsl:value-of select="jUnitReportpath" />
                                    </xsl:attribute>
                                    <xsl:text>JUnit-Report</xsl:text>
                                </xls:element>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
