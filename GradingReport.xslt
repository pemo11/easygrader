<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    version="1.0">
    <xsl:template match="/">
        <html>
            <body>
                <h3>Grading-Report</h3>
                <table border="1">
                    <tr bgcolor="#9acd32">
                        <th>Type</th>
                        <th>Student</th>
                        <th>Description</th>
                        <th>Result</th>
                        <th>Success</th>
                    </tr>
                    <xsl:for-each select="//gradeAction">
                        <tr>
                            <td><xsl:value-of select="type"/></td>
                            <td><xsl:value-of select="student"/></td>
                            <td><xsl:value-of select="description"/></td>
                            <td><xsl:value-of select="gradeResult"/></td>
                            <td><xsl:value-of select="gradeSuccess"/></td>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
