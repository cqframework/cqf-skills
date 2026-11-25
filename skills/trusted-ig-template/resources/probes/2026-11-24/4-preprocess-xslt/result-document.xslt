<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text"/>
  <xsl:template match="/">
    <xsl:result-document href="side-output.txt" method="text">a second output</xsl:result-document>
    <xsl:text>main output</xsl:text>
  </xsl:template>
</xsl:stylesheet>
