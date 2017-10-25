<?xml version="1.0"?>

<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
        <xsl:for-each select="lfm/album">
            <album>
                <name>
                    <xsl:value-of select="name"/>
                </name>
                <mbid>
                    <xsl:value-of select="mbid"/>
                </mbid>
                <image>
                    <xsl:value-of select="image[@size='mega']"/>
                </image>
                <wikiShort>
                    <xsl:value-of select="wiki/summary"/>
                </wikiShort>
                <wikiFull>
                    <xsl:value-of select="wiki/content"/>
                </wikiFull>
                <tracks>
                    <xsl:for-each select="tracks/track">
                        <track>
                            <name>
                                <xsl:value-of select="name"/>
                            </name>
                        </track>
                    </xsl:for-each>
                </tracks>
                <tags>
                    <xsl:for-each select="tags/tag">
                        <tag>
                            <xsl:value-of select="name"/>
                        </tag>
                    </xsl:for-each>
                </tags>
                <comments>
                </comments>
            </album>
        </xsl:for-each>
    </xsl:template>

</xsl:transform>