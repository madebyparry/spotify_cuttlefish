import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia('Spotify Cuttlefish (nicholas@madebyparry.com)', 'en')

def getWikiSelection(artist_name):
    try:
        artist_name.replace(' ', '_')
        artist_wiki = wiki_wiki.page(artist_name)
        if artist_wiki.exists() == False:
            artist_wiki = altWikiName(artist_name)
            return artist_wiki
        return artist_wiki
    except:
        return 

def altWikiName(invalid_artist_name):
        # Make more specific
        # if artist_wiki.summary == artist_name + ' may refer to:':
        print('No wiki page found for ' + invalid_artist_name)
        print('Trying others...\n')
        artist_wiki = wiki_wiki.page(invalid_artist_name)
        known_exceptions = [
            'Jazztet',
            'Septet',
            'Sextet',
            'Quartet',
            'Quintet',
            'Trio',
            'And His Orchestra',
            '& His Orchestra',
            'Band'
        ]
        for i in known_exceptions:
            if i in invalid_artist_name:
                new_artist_name = invalid_artist_name.replace(i,'')
                artist_wiki = wiki_wiki.page(new_artist_name)
            if artist_wiki.exists() == True:
                return artist_wiki


def getWiki(artist_name, addendums=False):
    # key returns
    #       artist_wiki._attributes
    #       artist_wiki.title
    #       artist_wiki.summary
    # handle exceptions:
    if addendums == True:
        addendums = [
            '(musician)',
            '(band)'
        ]
        for i in addendums:
            artist_name = artist_name + '_' + i
            artist_wiki = wiki_wiki.page(artist_name)
            if artist_wiki.exists():
                return artist_wiki
    if artist_wiki.exists() == True:
        return artist_wiki

def wikiSectionsGenerate(artist_wiki):
    wiki_sections = []
    c = 0
    for i in artist_wiki.sections:
        section_tuple = (i.title, c)
        wiki_sections.append(section_tuple)
        c += 1
    return wiki_sections


def printWikiResults(artist_wiki):
    # artist_wiki = getWiki(playing)
    artist_wiki = getWikiSelection(artist_wiki)
    print(artist_wiki.summary)
    return artist_wiki

def wikiSummary(artist_wiki):
    return artist_wiki.summary
