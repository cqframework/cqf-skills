<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:f="http://hl7.org/fhir" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="UTF-8"/>
  <xsl:template match="f:ImplementationGuide">
    <xsl:text>{"resources":</xsl:text>
    <xsl:value-of select="count(f:definition/f:resource)"/>
    <xsl:text>}</xsl:text>
  </xsl:template>
</xsl:stylesheet>
