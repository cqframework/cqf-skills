<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:f="http://hl7.org/fhir" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="UTF-8"/>
  <xsl:template match="f:ImplementationGuide">
    <xsl:if test="f:fhirVersion/@value[starts-with(., '4.')]">R4=Y&#xa;</xsl:if>
    <xsl:value-of select="concat('igVersion=', f:version/@value, '&#xa;')"/>
    <xsl:value-of select="concat('igTitle=', f:title/@value, '&#xa;')"/>
  </xsl:template>
</xsl:stylesheet>
