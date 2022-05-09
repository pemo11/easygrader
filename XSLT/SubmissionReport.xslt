<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    version="1.0">
    <xsl:template match="/">
        <html>
             <head>
                <meta charset="UTF-8" />
                <link href="Simpelgrader.css" type="text/css" rel="stylesheet" />
            </head>
           <body>
                <h3>Submission-Report</h3>
                <xsl:for-each select="//submission">
                    <table id="infoTable">
                        <tr><td>Student</td><td><xsl:value-of select="student"/></td></tr>
                        <tr><td>Exercise</td><td><xsl:value-of select="exercise"/></td></tr>
                        <tr><td>Number tests</td><td><xsl:value-of select="testcount"/></td></tr>
                        <tr><td>Total points</td><td><xsl:value-of select="totalPoints"/></td></tr>
                        <tr><td>Action summary</td><td><xsl:value-of select="actionSummary"/></td></tr>
                        <tr><td>Test summary</td><td><xsl:value-of select="testSummary"/></td></tr>
                        <tr><td>Feedback summary</td><td><xsl:value-of select="feedbackSummary"/></td></tr>
                    </table>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
