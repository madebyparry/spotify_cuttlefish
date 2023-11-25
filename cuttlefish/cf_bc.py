from bandcamp_api import Bandcamp

bc = Bandcamp()

def search_artist(artist_name):
    bandcamp_artist = ''
    bcr_artists = []
    bandcamp_results = bc.search(search_string=artist_name)
    for i in bandcamp_results:
        if (i.type == 'artist'):
            bcr_artists.append(i)
    if len(bcr_artists) > 0:
        for i in bcr_artists:
            print(i.artist_title)
        bandcamp_artist = bcr_artists[0]
        print(bandcamp_artist.__dir__())
        print(bandcamp_artist.artist_id)
        bcr_album = bc.get_album(artist_id=bandcamp_artist.artist_id)
        print(bcr_album)
        #for i in bcr_album:
        #    print('\t album - ' + i.album_title)
    return bandcamp_artist

