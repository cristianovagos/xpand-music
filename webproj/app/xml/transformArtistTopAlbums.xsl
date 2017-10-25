<?xml version="1.0"?>

<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
        <xsl:for-each select="lfm/topalbums/album">
            <topAlbum>
                <name>
                    <xsl:value-of select="name"/>
                </name>
                <image>
                    <xsl:value-of select="image[@size='extralarge']"/>
                </image>
            </topAlbum>
        </xsl:for-each>
    </xsl:template>

</xsl:transform>