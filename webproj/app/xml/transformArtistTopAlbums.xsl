<?xml version="1.0"?>

<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
        <topAlbums>
            <xsl:for-each select="lfm/topalbums/album">
                <topAlbum>
                    <name><xsl:value-of select="name"/></name>
                    <image>
                        <xsl:choose>
                            <xsl:when test="image[@size='extralarge'] != ''"><xsl:value-of select="image[@size='extralarge']"/></xsl:when>
                            <xsl:otherwise>https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png</xsl:otherwise>
                        </xsl:choose>
                    </image>
                </topAlbum>
            </xsl:for-each>
        </topAlbums>
    </xsl:template>

</xsl:transform>