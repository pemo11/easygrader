<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    version="1.0">
    <xsl:param name="student"/>
    <xsl:param name="exercise"/>
    <xsl:template match="report">
        <html>
             <head>
                <meta charset="UTF-8" />
                <link href="SubmissionFeedbackReport.css" type="text/css" rel="stylesheet" />
            </head>
           <body>
                <h3>Submission-Feedback for <xsl:value-of select="$student"/>/<xsl:value-of select="$exercise"/></h3>
                <table>
                    <tr><td>Anzahl Tests:</td><td><xsl:value-of select="testCount"/></td></tr>
                    <tr><td>Anzahl Punkte:</td><td><xsl:value-of select="totalPoints"/></td></tr>
                    <tr><td>Feedback:</td><td><xsl:value-of select="feedbackSummary"/></td></tr>
                </table>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
