<?xml version="1.0"?>

<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
        <xsl:for-each select="lfm/artist">
            <artist>
                <name>
                    <xsl:value-of select="name"/>
                </name>
                <mbid>
                    <xsl:value-of select="mbid"/>
                </mbid>
                <image>
                    <xsl:value-of select="image[@size='mega']"/>
                </image>
                <bioShort>
                    <xsl:value-of select="bio/summary"/>
                </bioShort>
                <bioFull>
                    <xsl:value-of select="bio/content"/>
                </bioFull>
                <similar>
                    <xsl:for-each select="similar/artist">
                        <similarartist>
                            <name>
                                <xsl:value-of select="name"/>
                            </name>
                            <image>
                                <xsl:value-of select="image[@size='mega']"/>
                            </image>
                        </similarartist>
                    </xsl:for-each>
                </similar>
                <albums>
                </albums>
                <tags>
                    <xsl:for-each select="tags/tag">
                        <tag>
                            <xsl:value-of select="name"/>
                        </tag>
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