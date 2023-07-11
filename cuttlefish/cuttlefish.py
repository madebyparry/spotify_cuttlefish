#!/usr/bin/env python3

import spotipy
import sys
import os
import inquirer
from time import sleep
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

def main():
    authenticateSpotipyOauth()
    initialSelection = [
    inquirer.List('initial_selection',
                    message="Cuttlefish options:",
                    choices=[
                        'player app',
                        'displayer app',
                        'next track',
                        'currently playing',
                        'current runtime',
                        'play/pause music',
                        'pause music',
                        'related artists',
                        'similar to playing',
                        'user top artists', 
                        'user playlists', 
                        ],
                ),
    ]
    userSelect = inquirer.prompt(initialSelection)
    triageSelection(userSelect["initial_selection"])

def setEnvVars():
    global sessionUser
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sessionUser = '73e213ujw0wxcy49bxwcfuhik'
    try:
        load_dotenv(dir_path[:-11] + '/data/.env')
    except:
        print('data/.env data not set.')

def authenticateSpotipyCreds():
    setEnvVars()
    global sp
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

def authenticateSpotipyOauth():
    scope = 'user-read-playback-state, user-modify-playback-state,user-read-currently-playing,user-top-read,streaming,playlist-read-private,user-follow-modify,user-read-recently-played,user-library-read'
    setEnvVars()
    global sp
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,open_browser=False))
    sp.devices()


def listUserPlaylists():
    print("list playlists")
    authenticateSpotipyCreds()
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

def relatedArtists():
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

def similarArtists():
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



def printCurrentRuntime():
    track_time = currentRuntime()
    running_time_sec = str(track_time['progress_seconds'])
    running_time_min = str(track_time['progress_minutes'])
    total_time_sec = str(track_time['duration_seconds'])
    total_time_min = str(track_time['duration_minutes'])
    pretty_print_time = running_time_min + ':' + running_time_sec + '/' + total_time_min + ':' + total_time_sec
    return pretty_print_time    

def currentlyPlaying():
    track = sp.current_user_playing_track()
    # 0, track name; 1, artist name; 2, album name
    playing = {}
    if not track is None:
        playing['album_art'] = track['item']['album']['images'][0]['url']
        playing['track_name'] = track['item']['name']
        playing['artist_name'] = track['item']['artists'][0]['name']
        playing['album_name'] = track['item']['album']['name']
        return playing
    else:
        playing['no_track'] = 'no track found :('
        return playing


def printCurrentlyPlaying():
    playing = currentlyPlaying()
    album_size = 80
    def catImg(album_art):
        os.system('wget -q ' + album_art)
        os.system('mv ' + album_art[24:] + ' data/album_art_cache')
        os.system('catimg -w ' + str(album_size) + ' data/album_art_cache')
    catImg(playing['album_art'])
    print(playing['artist_name'] + " - " + playing['album_name'])
    print(playing['track_name'])

def playPauseMusic():
    track = sp.currently_playing()
    if track['is_playing'] is False:
        sp.start_playback()
    else: 
        sp.pause_playback()

def playMusic():
    sp.start_playback()

def pauseMusic():
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
    elif user_choice == 'similar to playing':
        similarArtists()
    elif user_choice == 'user top artists':
        userTopArtists()
    elif user_choice == 'user playlists':
        listUserPlaylists()
    elif user_choice == 'currently playing':
        print(printCurrentlyPlaying())
    elif user_choice == 'play/pause music':
        playPauseMusic()
    elif user_choice == 'next track':
        nextTrack()
    elif user_choice == 'pause music':
        pauseMusic()
    elif user_choice == 'current runtime':
        print(printCurrentRuntime())
    else:
        print(user_choice)

if __name__ == "__main__":
    main()
