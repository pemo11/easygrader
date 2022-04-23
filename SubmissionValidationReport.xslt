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
                <link href="SubmissionValidation.css" type="text/css" rel="stylesheet" />
            </head>
            <body>
                <h3>Submission-Validation-Report <xsl:value-of select="$gradingTime"/> </h3>
                <table id="entries">
                    <tr bgcolor="#9acd32">
                        <th>Timestamp</th>
                        <th>Submission</th>
                        <th>Student</th>
                        <th>Exercise</th>
                        <th>Type</th>
                        <th>Message</th>
                    </tr>
                    <xsl:for-each select="//submissionValidation">
                        <xsl:variable name="trClass">
                          <xsl:choose>
                                <xsl:when test="type = 'Error'">
                                    <xsl:value-of select="'error'" />
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="'ok'" />
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:variable>
                        <tr class="{$trClass}" >
                            <td><xsl:value-of select="timestamp"/></td>
                            <td><xsl:value-of select="submissionId"/></td>
                            <td><xsl:value-of select="studentId"/></td>
                            <td><xsl:value-of select="exercise"/></td>
                            <td><xsl:value-of select="type"/></td>
                            <td><xsl:value-of select="message"/></td>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
