<?xml version="1.0" encoding="UTF-8"?>
<!-- A pre-process transform: one file, since includes don't work there. -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="@*|node()">
    <xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy>
  </xsl:template>
  <!-- Headings get an anchor id. -->
  <xsl:template match="h2[not(@id)]">
    <h2 id="{translate(normalize-space(.), ' ', '-')}"><xsl:apply-templates select="@*|node()"/></h2>
  </xsl:template>
</xsl:stylesheet>
