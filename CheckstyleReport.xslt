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
                <h3>Checkstyle-Report für <xsl:value-of select="$student"/>/<xsl:value-of select="$exercise"/></h3>
                <table id="entries">
                    <tr bgcolor="#9acd32">
                        <th>Nr</th>
                        <th>Zeile</th>
                        <th>Schweregrad</th>
                        <th>Problem</th>
                    </tr>
                    <xsl:for-each select="//file">
                        <h3><xsl:value-of select="name"/></h3>
                        <xsl:for-each select="//error">
                            <tr>
                                <td><xsl:number value="position()" /></td>
                                <td><xsl:value-of select="@line"/></td>
                                <xsl:choose>
                                    <xsl:when test="@severity='high'">
                                        <td style="background-color:orange"><xsl:value-of select="@severity"/></td>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <td bgcolor='lightgrey'><xsl:value-of select="@severity"/></td>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <td><xsl:value-of select="@message"/></td>
                            </tr>
                        </xsl:for-each>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
