<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="UTF-8"/>
  <xsl:template match="/">
    <xsl:text>{"resourceType":"OperationOutcome","issue":[</xsl:text>
    <xsl:if test="not(//li)">{"severity":"warning","code":"business-rule","diagnostics":"The menu is empty"}</xsl:if>
    <xsl:text>]}</xsl:text>
  </xsl:template>
</xsl:stylesheet>
