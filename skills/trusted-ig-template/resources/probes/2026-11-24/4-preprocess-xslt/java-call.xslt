<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:sys="java:java.lang.System">
  <xsl:output method="text"/>
  <xsl:template match="/">java.version=<xsl:value-of select="sys:getProperty('java.version')"/></xsl:template>
</xsl:stylesheet>
