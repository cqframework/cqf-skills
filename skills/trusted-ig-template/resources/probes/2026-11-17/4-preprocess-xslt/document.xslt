<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text"/>
  <xsl:template match="/">read: <xsl:value-of select="document('single.xslt')"/></xsl:template>
</xsl:stylesheet>
