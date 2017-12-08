<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <xsl:for-each select="lfm/artist">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                     xmlns:foaf="http://xmlns.com/foaf/0.1/"
                     xmlns:cs="http://www.xpand.com/rdf/">

                <!-- Obter nome do artista a partir do URL do xml para preencher o ID para RDF -->
                <xsl:variable name="artistURL">
                    <xsl:value-of select="substring-after(url, 'https://www.last.fm/music/')"/>
                </xsl:variable>

                <!-- Inicio da descricao do artista -->
                <cs:MusicArtist rdf:about="http://www.xpand.com/artists/{$artistURL}">
                    <!-- Nome -->
                    <foaf:name>
                        <xsl:value-of select="name"/>
                    </foaf:name>

                    <!-- Imagem -->
                    <foaf:Image>
                        <xsl:choose>
                            <xsl:when test="image[@size='mega'] != ''">
                                <xsl:value-of select="image[@size='mega']"/>
                            </xsl:when>
                            <xsl:otherwise>http://paradeal.pp.ua/img/no-user.jpg</xsl:otherwise>
                        </xsl:choose>
                    </foaf:Image>

                    <!-- Biografia -->
                    <cs:biography>
                        <xsl:choose>
                            <xsl:when test="bio/summary != ''">
                                <xsl:value-of
                                        select="substring-before(bio/summary, '&lt;a href=')"/>
                            </xsl:when>
                            <xsl:otherwise>Sorry, the artist biography is not available.</xsl:otherwise>
                        </xsl:choose>
                    </cs:biography>

                    <!-- Contador de plays -->
                    <cs:playCount>
                        <xsl:value-of select="stats/playcount"/>
                    </cs:playCount>

                    <!-- Artistas similares (sem inferencia) -->
                    <!--
                    <xsl:for-each select="similar/artist">
                        <cs:similarArtist>
                            http://www.xpand.com/artists#<xsl:value-of select="substring-after(url, 'https://www.last.fm/music/')"/>
                        </cs:similarArtist>
                    </xsl:for-each>
                    -->

                    <!-- Tags -->
                    <xsl:for-each select="tags/tag">
                        <cs:Tag>http://www.xpand.com/tags/<xsl:value-of select="translate(name,' ','')"/></cs:Tag>
                    </xsl:for-each>
                </cs:MusicArtist>

                <xsl:for-each select="tags/tag">
                    <xsl:variable name="tagURL">
                        <xsl:value-of select="translate(name,' ','')"/>
                    </xsl:variable>

                    <cs:Tag rdf:about="http://www.xpand.com/tags/{$tagURL}">
                        <foaf:name>
                            <xsl:value-of select="name"/>
                        </foaf:name>
                    </cs:Tag>
                </xsl:for-each>
            </rdf:RDF>
        </xsl:for-each>
    </xsl:template>
</xsl:transform>