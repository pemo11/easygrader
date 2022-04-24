<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    version="1.0">
    <xsl:param name="semester"/>
    <xsl:param name="module"/>
    <xsl:param name="exercise"/>
    <xsl:param name="gradingTime"/>
    <xsl:template match="/">
        <html>
             <head>
                <meta charset="UTF-8" />
                <link href="GradingReport.css" type="text/css" rel="stylesheet" />
            </head>
           <body>
                <h3>Grading-Report <xsl:value-of select="$gradingTime"/> - <xsl:value-of select="$module"/>/<xsl:value-of select="$exercise"/> (<xsl:value-of select="$semester"/>)</h3>
                <table id="entries">
                    <tr bgcolor="#9acd32">
                        <th>Timestamp</th>
                        <th>Type</th>
                        <th>Student</th>
                        <th>Description</th>
                        <th>Message</th>
                        <th>Points</th>
                        <th>Success</th>
                    </tr>
                    <xsl:for-each select="//gradeResult">
                        <tr>
                            <td><xsl:value-of select="timestamp"/></td>
                            <td><xsl:value-of select="type"/></td>
                            <td><xsl:value-of select="student"/></td>
                            <td><xsl:value-of select="description"/></td>
                            <td><xsl:value-of select="message"/></td>
                            <td><xsl:value-of select="points"/></td>
                            <xsl:choose>
                                <xsl:when test="gradeSuccess = 'False'">
                                    <td style="background-color:orange"><xsl:value-of select="gradeSuccess"/></td>
                                </xsl:when>
                                <xsl:otherwise>
                                    <td bgcolor='lightgrey'><xsl:value-of select="gradeSuccess"/></td>
                                </xsl:otherwise>
                            </xsl:choose>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
