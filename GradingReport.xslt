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
            <body>
                <h3>Grading-Report <xsl:value-of select="$gradingTime"/> - <xsl:value-of select="$module"/>/<xsl:value-of select="$exercise"/> (<xsl:value-of select="$semester"/>)</h3>
                <table border="1">
                    <tr bgcolor="#9acd32">
                        <th>Type</th>
                        <th>Timestamp</th>
                        <th>Student</th>
                        <th>Description</th>
                        <th>Result</th>
                        <th>Success</th>
                    </tr>
                    <xsl:for-each select="//gradeAction">
                        <tr>
                            <td><xsl:value-of select="type"/></td>
                            <td><xsl:value-of select="timestamp"/></td>
                            <td><xsl:value-of select="student"/></td>
                            <td><xsl:value-of select="description"/></td>
                            <td><xsl:value-of select="gradeResult"/></td>
                            <xsl:choose>
                                <xsl:when test="gradeSuccess = 'False'">
                                    <td bgcolor='red'><xsl:value-of select="gradeSuccess"/></td>
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
