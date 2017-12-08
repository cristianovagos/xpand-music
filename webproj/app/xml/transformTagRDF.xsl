<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <xsl:for-each select="lfm/tag">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                     xmlns:foaf="http://xmlns.com/foaf/0.1/"
                     xmlns:cs="http://www.xpand.com/rdf/">

                <xsl:variable name="tagTrimmed">
                    <xsl:value-of select="translate(name,' ','')"/>
                </xsl:variable>

                <cs:Tag rdf:about="http://www.xpand.com/tags/{$tagTrimmed}">
                    <foaf:name>
                        <xsl:value-of select="name"/>
                    </foaf:name>

                    <!-- Contador de plays -->
                    <cs:playCount>
                        <xsl:value-of select="total"/>
                    </cs:playCount>

                    <!-- Biografia da tag -->
                    <cs:biography>
                        <xsl:choose>
                            <xsl:when test="wiki/summary != ''">
                                <xsl:value-of
                                        select="substring-before(wiki/summary, '&lt;a href=')"/>
                            </xsl:when>
                            <xsl:otherwise>Sorry, the artist biography is not available.</xsl:otherwise>
                        </xsl:choose>
                    </cs:biography>
                </cs:Tag>

            </rdf:RDF>
        </xsl:for-each>
    </xsl:template>
</xsl:transform>