<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <xsl:for-each select="lfm/track">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                     xmlns:foaf="http://xmlns.com/foaf/0.1/"
                     xmlns:cs="http://www.xpand.com/rdf/">

                <xsl:variable name="artistURL">
                    <xsl:value-of select="substring-after(artist/url, 'https://www.last.fm/music/')"/>
                </xsl:variable>

                <xsl:variable name="trackNameTrimmed">
                    <xsl:value-of select="translate(name,' ','')"/>
                </xsl:variable>

                <xsl:variable name="trackName">
                    <xsl:value-of select="name"/>
                </xsl:variable>

                <cs:Track rdf:about="http://www.xpand.com/track/{$artistURL}/{$trackNameTrimmed}">
                    <!-- Tags -->
                    <xsl:for-each select="toptags/tag">
                        <cs:Tag>http://www.xpand.com/tags/<xsl:value-of select="translate(name,' ','')"/></cs:Tag>
                    </xsl:for-each>

                    <!-- Contador de plays -->
                    <cs:playCount>
                        <xsl:value-of select="playcount"/>
                    </cs:playCount>

                    <!-- Biografia do album -->
                    <cs:biography>
                        <xsl:choose>
                            <xsl:when test="wiki/summary != ''">
                                <xsl:value-of
                                        select="substring-before(wiki/summary, '&lt;a href=')"/>
                            </xsl:when>
                            <xsl:otherwise>Sorry, the artist biography is not available.</xsl:otherwise>
                        </xsl:choose>
                    </cs:biography>
                </cs:Track>

            </rdf:RDF>
        </xsl:for-each>
    </xsl:template>
</xsl:transform>