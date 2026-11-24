<?xml version="1.0" encoding="UTF-8"?>
<!-- The footer stamp. value-of escapes the IG's version for HTML, so it is only ever text. -->
<xsl:stylesheet version="1.0" xmlns:f="http://hl7.org/fhir" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" omit-xml-declaration="yes"/>
  <xsl:template match="f:ImplementationGuide">
    <span class="stamp">Version <xsl:value-of select="normalize-space(f:version/@value)"/></span>
  </xsl:template>
</xsl:stylesheet>
