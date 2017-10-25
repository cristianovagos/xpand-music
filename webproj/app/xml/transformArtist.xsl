<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <xsl:for-each select="lfm/artist">
            <artist>
                <name><xsl:value-of select="name"/></name>
                <mbid><xsl:value-of select="mbid"/></mbid>
                <image>
                    <xsl:choose>
                        <xsl:when test="image[@size='mega'] != ''"><xsl:value-of select="image[@size='mega']"/></xsl:when>
                        <xsl:otherwise>http://paradeal.pp.ua/img/no-user.jpg</xsl:otherwise>
                    </xsl:choose>
                </image>
                <bioShort>
                    <xsl:choose>
                        <xsl:when test="bio/summary != ''"><xsl:value-of select="bio/summary"/></xsl:when>
                        <xsl:otherwise>Sorry, the artist biography is not available.</xsl:otherwise>
                    </xsl:choose>
                </bioShort>
                <bioFull>
                    <xsl:choose>
                        <xsl:when test="bio/content != ''"><xsl:value-of select="bio/content"/></xsl:when>
                        <xsl:otherwise>Sorry, the artist biography is not available.</xsl:otherwise>
                    </xsl:choose>
                </bioFull>
                <similar>
                    <xsl:for-each select="similar/artist">
                        <similarartist>
                            <name><xsl:value-of select="name"/></name>
                            <image>
                                <xsl:choose>
                                    <xsl:when test="image[@size='mega'] != ''"><xsl:value-of select="image[@size='mega']"/></xsl:when>
                                    <xsl:otherwise>http://paradeal.pp.ua/img/no-user.jpg</xsl:otherwise>
                                </xsl:choose>
                            </image>
                        </similarartist>
                    </xsl:for-each>
                </similar>
                <albums>
                </albums>
                <tags>
                    <xsl:for-each select="tags/tag">
                        <tag><xsl:value-of select="name"/></tag>
                    </xsl:for-each>
                </tags>
                <topAlbums>
                </topAlbums>
                <topTracks>
                </topTracks>
                <comments>
                </comments>
            </artist>
        </xsl:for-each>
    </xsl:template>
</xsl:transform>