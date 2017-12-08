<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <xsl:for-each select="lfm/album">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                     xmlns:foaf="http://xmlns.com/foaf/0.1/"
                     xmlns:cs="http://www.xpand.com/rdf/">

                <!-- Obter nome do artista e do album a partir do URL do xml para preencher o ID para RDF -->
                <xsl:variable name="dataURL">
                    <xsl:value-of select="substring-after(url, 'https://www.last.fm/music/')"/>
                </xsl:variable>

                <xsl:variable name="artistURL">
                    <xsl:value-of select="substring-before($dataURL, '/')"/>
                </xsl:variable>

                <xsl:variable name="albumURL">
                    <xsl:value-of select="substring-after($dataURL, '/')"/>
                </xsl:variable>

                <!-- Inicio da descricao do album -->
                <cs:Album rdf:about="http://www.xpand.com/album/{$dataURL}">
                    <cs:MusicArtist>http://www.xpand.com/artists/<xsl:value-of select="$artistURL"/></cs:MusicArtist>

                    <!-- Nome -->
                    <foaf:name>
                        <xsl:value-of select="name"/>
                    </foaf:name>

                    <!-- Imagem -->
                    <foaf:Image>
                        <xsl:choose>
                            <xsl:when test="image[@size='extralarge'] != ''">
                                <xsl:value-of select="image[@size='extralarge']"/>
                            </xsl:when>
                            <xsl:otherwise>https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png</xsl:otherwise>
                        </xsl:choose>
                    </foaf:Image>

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
                    
                    <!-- Contador de plays -->
                    <cs:playCount>
                        <xsl:value-of select="playcount"/>
                    </cs:playCount>

                    <!-- Tags -->
                    <xsl:for-each select="tags/tag">
                        <cs:Tag>http://www.xpand.com/tags/<xsl:value-of select="translate(name,' ','')"/></cs:Tag>
                    </xsl:for-each>
                </cs:Album>
                
                <!-- Tracks -->
                <xsl:for-each select="tracks/track">
                    <xsl:variable name="trackNameTrimmed">
                        <xsl:value-of select="translate(name,' ','')"/>
                    </xsl:variable>

                    <xsl:variable name="trackName">
                        <xsl:value-of select="name"/>
                    </xsl:variable>
                   
                    <cs:Track rdf:about="http://www.xpand.com/track/{$artistURL}/{$trackNameTrimmed}">
                        <cs:Album>http://www.xpand.com/album/<xsl:value-of select="$dataURL"/></cs:Album>
                        <xsl:for-each select="artist">
                            <cs:MusicArtist>http://www.xpand.com/artists/<xsl:value-of select="substring-after(url, 'https://www.last.fm/music/')"/></cs:MusicArtist>
                        </xsl:for-each>
                        <foaf:name>
                            <xsl:value-of select="$trackName"/>
                        </foaf:name>
                        <cs:duration>
                            <xsl:value-of select="duration"/>
                        </cs:duration>
                    </cs:Track>
                </xsl:for-each>
            </rdf:RDF>
        </xsl:for-each>
    </xsl:template>
</xsl:transform>