<?xml version="1.0"?>

<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
        <xsl:for-each select="lfm/album">
            <album>
                <name><xsl:value-of select="name"/></name>
                <mbid><xsl:value-of select="mbid"/></mbid>
                <image>
                    <xsl:choose>
                        <xsl:when test="image[@size='mega'] != ''"><xsl:value-of select="image[@size='mega']"/></xsl:when>
                        <xsl:otherwise>https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png</xsl:otherwise>
                    </xsl:choose>
                </image>
                <wikiShort>
                    <xsl:choose>
                        <xsl:when test="wiki/summary != ''"><xsl:value-of select="wiki/summary"/></xsl:when>
                        <xsl:otherwise>Sorry, the artist biography is not available.</xsl:otherwise>
                    </xsl:choose>
                </wikiShort>
                <wikiFull>
                    <xsl:choose>
                        <xsl:when test="wiki/content != ''"><xsl:value-of select="wiki/content"/></xsl:when>
                        <xsl:otherwise>Sorry, the artist biography is not available.</xsl:otherwise>
                    </xsl:choose>
                </wikiFull>
                <tracks>
                    <xsl:for-each select="tracks/track">
                        <track>
                            <name><xsl:value-of select="name"/></name>
                        </track>
                    </xsl:for-each>
                </tracks>
                <tags>
                    <xsl:for-each select="tags/tag">
                        <tag><xsl:value-of select="name"/></tag>
                    </xsl:for-each>
                </tags>
                <comments>
                </comments>
            </album>
        </xsl:for-each>
    </xsl:template>

</xsl:transform>