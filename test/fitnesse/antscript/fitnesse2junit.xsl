<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- from Daniel A. Woodward http://whotestedthis.squarespace.com/ -->
<xsl:template match="/">
 <xsl:element name="testsuite">
   <xsl:attribute name="tests">
     <xsl:value-of select="sum(suiteResults/finalCounts/*)" />
   </xsl:attribute>
   <xsl:attribute name="failures">
     <xsl:value-of select="suiteResults/finalCounts/wrong" />
   </xsl:attribute>
   <xsl:attribute name="disabled">
     <xsl:value-of select="suiteResults/finalCounts/ignores" />
   </xsl:attribute>
   <xsl:attribute name="errors">
     <xsl:value-of select="suiteResults/finalCounts/exceptions" />
   </xsl:attribute>
   <xsl:attribute name="name"><xsl:value-of select="/suiteResults/rootPath" /></xsl:attribute>
 <xsl:for-each select="suiteResults/pageHistoryReference">
   <xsl:element name="testcase">
     <xsl:attribute name="classname">
       <xsl:value-of select="/suiteResults/rootPath" />
     </xsl:attribute>
     <xsl:attribute name="name">
       <xsl:value-of select="name" />
     </xsl:attribute>
     <xsl:attribute name="time">
       <xsl:value-of select="runTimeInMillis div 1000" />
     </xsl:attribute>
     <xsl:choose>
       <xsl:when test="counts/exceptions > 0">
         <xsl:element name="error">
           <xsl:attribute name="message">
             <xsl:value-of select="counts/exceptions" />
             <xsl:text> exceptions thrown</xsl:text>
             <xsl:if test="counts/wrong > 0">
               <xsl:text> and </xsl:text>
               <xsl:value-of select="counts/wrong" />
               <xsl:text> assertions failed</xsl:text>
             </xsl:if>
           </xsl:attribute>
         </xsl:element>
       </xsl:when>
       <xsl:when test="counts/wrong > 0">
         <xsl:element name="failure">
           <xsl:attribute name="message">
             <xsl:value-of select="counts/wrong" />
             <xsl:text> assertions failed</xsl:text>
           </xsl:attribute>
         </xsl:element>
       </xsl:when>
     </xsl:choose>
   </xsl:element>
 </xsl:for-each>
 </xsl:element>
</xsl:template>
</xsl:stylesheet>