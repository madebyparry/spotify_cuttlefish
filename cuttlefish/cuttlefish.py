#!/usr/bin/env python3

import spotipy
import sys
import os
import inquirer
from cf_wiki import wikiSectionsGenerate, wikiSummary, getWikiSelection
from time import sleep
from dotenv import load_dotenv, dotenv_values
from spotipy import oauth2
from bottle import route, run, request
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

@route('/')
def main():
    setEnvVars()
    initialSelection = [
    inquirer.List('initial_selection',
                    message="Cuttlefish options:",
                    choices=[
                        'currently playing',
                        'check wiki',
                        'current runtime',
                        'play/pause music',
                        'next track',
                        'related artists',
                        'search related',
                        'user top artists', 
                        'user playlists', 
                        'player app',
                        'displayer app',
                        'shutdown'
                        ],
                ),
    ]
    userSelect = inquirer.prompt(initialSelection)
    triageSelection(userSelect["initial_selection"])

def setEnvVars():
    global sp
    global sessionUser
    global SPOTIPY_CLIENT_ID
    global SPOTIPY_CLIENT_SECRET
    global SPOTIPY_REDIRECT_URI
    global sp_oauth
    sys_user_home = os.path.expanduser('~')
    dir_path = sys_user_home + '/spotify_cuttlefish/cuttlefish'
    env_file = dir_path[:-11] + '/data/.env'
    auth_cache = dir_path[:-11] + '/data/.cache'
    sessionUser = '73e213ujw0wxcy49bxwcfuhik'
    try:
        load_dotenv(env_file)
        env_vals = dotenv_values(env_file)
        SPOTIPY_CLIENT_ID = env_vals['SPOTIPY_CLIENT_ID']
        SPOTIPY_CLIENT_SECRET = env_vals['SPOTIPY_CLIENT_SECRET']
        SPOTIPY_REDIRECT_URI = env_vals['SPOTIPY_REDIRECT_URI']
    except:
        print('Spotipy says: data/.env data not set ;-(')
    access_token = ''
    scope = 'user-read-playback-state, user-modify-playback-state,user-read-currently-playing,user-top-read,streaming,playlist-read-private,user-follow-modify,user-read-recently-played,user-library-read'
    sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope)
    token_cache = sp_oauth.get_cached_token()
    if token_cache != True:
        served_url = request.url
        oauth_request_code = sp_oauth.parse_response_code(served_url)
        if oauth_request_code != served_url:
            token_cache = sp_oauth.get_access_token(oauth_request_code)
            access_token = token_cache
    # if access_token:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope, cache_path=auth_cache, username=sessionUser, open_browser= False))
    sp.devices()
    # else:
        # authenticateSpotipyOauth()
        # run(host='localhost', port=9088)



def authenticateSpotipyCreds():
    global sp
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

def authenticateSpotipyOauth():
    auth_url = sp_oauth.get_authorize_url()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton


def listUserPlaylists():
    print("list playlists")
    # authenticateSpotipyCreds()
    playlists = sp.user_playlists(sessionUser)
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
        
def userTopArtists():
    print("top artists")
    ranges = ['short_term', 'medium_term', 'long_term']
    for sp_range in ranges:
        print("range:", sp_range)
        results = sp.current_user_top_artists(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            print(i, item['name'])
        print()

def searchRelated():
    print("related artists")
    artist_name = input("Related to whom? >> ")
    authenticateSpotipyCreds()
    result = sp.search(q='artist:' + artist_name, type='artist')
    try:
        name = result['artists']['items'][0]['name']
        uri = result['artists']['items'][0]['uri']

        related = sp.artist_related_artists(uri)
        print('Related artists for', name)
        for artist in related['artists']:
            print('  ', artist['name'])
    except BaseException:
        print("No related artists: " + artist_name)

def relatedArtists():
    print("similar artists")
    authenticateSpotipyCreds()
    track = sp.current_user_playing_track()
    artist_name = track['item']['artists'][0]['name']
    result = sp.search(q='artist:' + artist_name, type='artist')
    try:
        name = result['artists']['items'][0]['name']
        uri = result['artists']['items'][0]['uri']

        related = sp.artist_related_artists(uri)
        print('Related artists for', name)
        for artist in related['artists']:
            print('  ', artist['name'])
    except BaseException:
        print("No related artists: " + artist_name)


def currentRuntime():
    track = sp.current_user_playing_track()
    def readableTime(ms):
        time = []
        x = ms / 1000
        seconds = x % 60
        x /= 60
        minutes = x % 60
        time.append(seconds)
        time.append(minutes)
        return time
    if not track is None:
        times = {}
        progress = readableTime(track['progress_ms'])
        duration = readableTime(track['item']['duration_ms'])
        times['progress_seconds'] = round(progress[0])
        times['progress_minutes'] = round(progress[1])
        times['duration_seconds'] = round(duration[0])
        times['duration_minutes'] = round(duration[1])
        return times
    else:
        return "No track currently playing." 

def sanitizeNamesUTF(input):
    output = input.encode(
        'utf-8', errors='ignore'
    ).decode('utf-8')
    return output

def printCurrentRuntime():
    track_time = currentRuntime()
    running_time_sec = str(track_time['progress_seconds'])
    running_time_min = str(track_time['progress_minutes'])
    total_time_sec = str(track_time['duration_seconds'])
    total_time_min = str(track_time['duration_minutes'])
    pretty_print_time = running_time_min + ':' + running_time_sec + '/' + total_time_min + ':' + total_time_sec
    return pretty_print_time    

def currentlyPlaying():
    try:
        track = sp.current_user_playing_track()
        playing = {}
        playing['album_art'] = track['item']['album']['images'][0]['url']
        playing['track_name'] = sanitizeNamesUTF(track['item']['name'])
        playing['artist_name'] = sanitizeNamesUTF(track['item']['artists'][0]['name'])
        playing['album_name'] = sanitizeNamesUTF(track['item']['album']['name'])
        return playing
    except:
        return playing


def printCurrentlyPlaying():
    playing = currentlyPlaying()
    if len(playing) > 0:
        runtime = printCurrentRuntime()
        album_size = 80
        def displayCatImg(album_art):
            os.system('wget -q ' + album_art)
            os.system('mv ' + album_art[24:] + ' data/album_art_cache')
            os.system('catimg -w ' + str(album_size) + ' data/album_art_cache')
        displayCatImg(playing['album_art'])
        print(playing['artist_name'] + " - " + playing['album_name'])
        print(playing['track_name'])
        print(runtime)
        sleep(2)
    else:
        print('| ----------------------------------')
        print('| Error:')
        print('| No track currently playing.')
        print('| ----------------------------------\n')
        sleep(1)


# def getWiki(addendums=False):
#     # key returns
#     #       artist_wiki._attributes
#     #       artist_wiki.title
#     #       artist_wiki.summary
#     artist_info = currentlyPlaying()
#     artist_name = artist_info['artist_name']
#     artist_name.replace(' ', '_')
#     artist_wiki = wiki_wiki.page(artist_name)
#     # handle exceptions:
#     if addendums == True:
#         addendums = [
#             '(musician)',
#             '(band)'
#         ]
#         for i in addendums:
#             artist_name = artist_info['artist_name']
#             artist_name = artist_name + '_' + i
#             artist_wiki = wiki_wiki.page(artist_name)
#             if artist_wiki.exists():
#                 return artist_wiki
#     if artist_wiki.exists() == True:
#         return artist_wiki
#     else: 
#         # Make more specific
#         # if artist_wiki.summary == artist_name + ' may refer to:':
#         print('No wiki page found for ' + artist_name)
#         print('Trying others...')
#         known_exceptions = [
#             'Jazztet',
#             'Septet',
#             'Sextet',
#             'Quartet',
#             'Quintet',
#             'Trio',
#             'And His Orchestra',
#             'Band'
#         ]
#         for i in known_exceptions:
#             if i in artist_name:
#                 x = artist_name.find(i)
#                 artist_name = artist_name.replace(i,'')
#                 artist_wiki = wiki_wiki.page(artist_name)
#             if artist_wiki.exists():
#                 return artist_wiki

# def wikiSectionSelector(artist_wiki):
#     # Generate inquirer list for sections
#     section_selections = []
#     c = 0
#     for i in artist_wiki.sections:
#         section_tuple = (i.title, c)
#         section_selections.append(section_tuple)
#         c += 1
#     return_tuple = ('-- RETURN --', 99)
#     section_selections.append(return_tuple)
#     sectionSelection = [
#         inquirer.List('selected_wiki_section',
#                         message="More about " + artist_wiki.title + " :",
#                         choices=section_selections,
#                     ),
#         ]
#     sectionSelected = inquirer.prompt(sectionSelection)
#     def printPretty(print_input, prepend=''):
#         c = 0
#         print(prepend, end='')
#         for i in print_input:
#             if c > 100 and i == ' ':
#                 print(i)
#                 print(prepend, end='')
#                 c = 0
#             elif i == '\n':
#                 print(i, end='')
#                 print(prepend, end='')
#                 c = 0
#             else:
#                 print(i, end='')
#                 c += 1
#         print('\n')
#     # Wiki logic
#     def printSectionsNested(sections):
#         for i in sections:
#             print('------- ' + i.title + ' -------')
#             printPretty(i.text, '\t')
#             printSectionsNested(i.sections)
#     if sectionSelected['selected_wiki_section'] == 99:
#         main()
#     else:
#         value = sectionSelected['selected_wiki_section']
#         key = section_selections[value][0]
#         # print(artist_wiki.section_by_title(key))
#         printSectionsNested(artist_wiki.sections_by_title(key))
#         wikiSectionSelector(artist_wiki)

# def printWikiResults():
#     global artist_wiki
#     artist_wiki = getWiki()
#     print(artist_wiki.summary)
#     if artist_wiki == None:
#         print('Could not find in Wikipedia - sorry!')

def printPretty(print_input, prepend=''):
    c = 0
    print(prepend, end='')
    for i in print_input:
        if c > 100 and i == ' ':
            print(i)
            print(prepend, end='')
            c = 0
        elif i == '\n':
            print(i, end='')
            print(prepend, end='')
            c = 0
        else:
            print(i, end='')
            c += 1
    print('\n')

def wikiSectionSelector(artist_wiki):
    # Generate inquirer list for sections
    section_selections = wikiSectionsGenerate(artist_wiki)
    return_tuple = ('-- RETURN --', 99)
    section_selections.append(return_tuple)
    sectionSelection = [
        inquirer.List('selected_wiki_section',
                        message="More about " + artist_wiki.title + " :",
                        choices=section_selections,
                    ),
        ]
    sectionSelected = inquirer.prompt(sectionSelection)
    def printSectionsNested(sections):
        for i in sections:
            print('------- ' + i.title + ' -------')
            printPretty(i.text, '\t')
            printSectionsNested(i.sections)
    if sectionSelected['selected_wiki_section'] == 99:
        return
    else:
        value = sectionSelected['selected_wiki_section']
        key = section_selections[value][0]
        printSectionsNested(artist_wiki.sections_by_title(key))
        wikiSectionSelector(artist_wiki)

def validateWiki():
    playing = currentlyPlaying()
    artist_wiki = getWikiSelection(playing['artist_name'])
    if artist_wiki:
        print('------- ' + artist_wiki.title + ' -------')
        printPretty(wikiSummary(artist_wiki), '\t')
        print('-------------------------------------------------\n')
        wikiSectionSelector(artist_wiki)
    else: 
        print('| ----------------------------------')
        print('| Error:')
        print('| No wikipedia page found for that search. ')
        print('| ----------------------------------\n')
        sleep(1)


def playPauseMusic():
    track = sp.currently_playing()
    if track['is_playing'] is False:
        sp.start_playback()
    else: 
        sp.pause_playback()

def nextTrack():
	sp.next_track()
        
def volumeControl():
    sp.volume(100)
    sleep(2)
    sp.volume(50)
    sleep(2)
    sp.volume(100)
        

def triageSelection(user_choice):
    if user_choice == 'related artists':
        relatedArtists()
        main()
    elif user_choice == 'search related':
        searchRelated()
        main()
    elif user_choice == 'user top artists':
        userTopArtists()
        main()
    elif user_choice == 'user playlists':
        listUserPlaylists()
        main()
    elif user_choice == 'currently playing':
        printCurrentlyPlaying()
        main()
    elif user_choice == 'play/pause music':
        playPauseMusic()
        main()
    elif user_choice == 'next track':
        nextTrack()
        main()
    elif user_choice == 'current runtime':
        print(printCurrentRuntime())
        main()
    elif user_choice == 'check wiki':
        validateWiki()
        main()
    elif user_choice == 'shutdown':
        print('Bye-bye!')
        return
    else:
        print(user_choice)
        print('Bye-bye!')
        return


if __name__ == "__main__":
    main()
