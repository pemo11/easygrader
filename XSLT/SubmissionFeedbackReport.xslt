<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    version="1.0">
    <xsl:template match="/">
        <html>
             <head>
                <meta charset="UTF-8" />
                <link href="SubmissionFeedbackReport.css" type="text/css" rel="stylesheet" />
            </head>
           <body>
                <xsl:for-each select="//" />
                <h3>Submission-Feedback for <xsl:value-of select="student"/>/<xsl:value-of select="exercise"/>/<xsl:value-of select="$exercise"/></h3>
                <xsl:value-of select="testCount"/>
                <xsl:value-of select="totalPoints"/>
                <xsl:value-of select="feedbackMessage"/>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
