<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    version="1.0">
    <xsl:param name="student"/>
    <xsl:param name="exercise"/>
    <xsl:template match="/">
        <html>
             <head>
                <meta charset="UTF-8" />
                <link href="Simpelgrader.css" type="text/css" rel="stylesheet" />
            </head>
           <body>
                <h3>JUnit-Report <xsl:value-of select="$student"/>/<xsl:value-of select="$exercise"/></h3>
                <table id="entries">
                    <tr bgcolor="#9acd32">
                        <th>Nr</th>
                        <th>Test</th>
                        <th>Result</th>
                        <th>ErrorCount</th>
                    </tr>
                    <xsl:for-each select="//test">
                        <tr>
                            <td><xsl:number value="position()" /></td>
                            <td><xsl:value-of select="test"/></td>
                            <td><xsl:value-of select="result"/></td>
                            <xsl:choose>
                                <xsl:when test="count(errors/error) > 0">
                                    <td style="background-color:orange"><xsl:value-of select="count(errors/error)"/></td>
                                </xsl:when>
                                <xsl:otherwise>
                                    <td bgcolor='lightgrey'><xsl:value-of select="count(errors/error)"/></td>
                                </xsl:otherwise>
                            </xsl:choose>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
