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
    initialSelection = [
    inquirer.List('initial_selection',
                    message="Cuttlefish options:",
                    choices=[
                        'next track',
                        'currently playing',
                        'current runtime',
                        'display on pi',
                        'play/pause music',
                        'pause music',
                        'related artists',
                        'similar to playing',
                        'user top artists', 
                        'user playlists', 
                        'gen test oauth'
                        ],
                ),
    ]
    userSelect = inquirer.prompt(initialSelection)
    triageSelection(userSelect["initial_selection"])

def authenticateSpotipyCreds():
    setEnvVars()
    global sp
    global sessionUser
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    sessionUser = '73e213ujw0wxcy49bxwcfuhik'

def authenticateSpotipyOauth(scope):
    setEnvVars()
    global sp
    global sessionUser
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,open_browser=False))
    sessionUser = '73e213ujw0wxcy49bxwcfuhik'

def setEnvVars():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    load_dotenv(dir_path[:-11] + '/data/.env')
    # env_cmd = 'source ' + dir_path[:-11] + '/data/.env'
    # print(env_cmd)
    # os.system(env_cmd)

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
    if not track is None:
        track_dur = track['item']['duration_ms']
        track_pro = track['progress_ms']
        print('Progress: ' + str(track_pro / track_dur))
        print('Duration: ' + str(0.001 * track_dur) + ' - Progress: ' + str(0.001 * track_pro))
    else:
        print("No track currently playing.") 


def currentlyPlaying():
    print("currently playing: \n")
    track = sp.current_user_playing_track()
    album_size = 80
    def catImg(album_art):
        os.system('wget -q ' + album_art)
        os.system('mv ' + album_art[24:] + ' data/album_art_cache')
        os.system('catimg -w ' + str(album_size) + ' data/album_art_cache')
    if not track is None:
        album_art = track['item']['album']['images'][0]['url']
        album_name = track['item']['album']['name']
        artist_name = track['item']['artists'][0]['name']
        track_name = track['item']['name']
        catImg(album_art)
        print(artist_name + " - " + album_name)
        print(track_name)
    else:
        print("No track currently playing.") 

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
        
def genTestOauth():
    displayCuttlefish()
    print(".cache generated")


def displayCuttlefish():
    pi_name = "192.168.0.201"
    print(pi_name)
    print(sp.devices())


def triageSelection(user_choice):
    scopes = 'user-read-playback-state, user-modify-playback-state,user-read-currently-playing,user-top-read,streaming,playlist-read-private,user-follow-modify,user-read-recently-played,user-library-read'
    authenticateSpotipyOauth(scopes)
    if user_choice == 'related artists':
        relatedArtists()
    elif user_choice == 'similar to playing':
        similarArtists()
    elif user_choice == 'user top artists':
        userTopArtists()
    elif user_choice == 'user playlists':
        listUserPlaylists()
    elif user_choice == 'currently playing':
        currentlyPlaying()
    elif user_choice == 'play/pause music':
        playPauseMusic()
    elif user_choice == 'display on pi':
        displayCuttlefish()
    elif user_choice == 'next track':
        nextTrack()
    elif user_choice == 'gen test oauth':
        genTestOauth()
    elif user_choice == 'pause music':
        pauseMusic()
    elif user_choice == 'current runtime':
        currentRuntime()
    else:
        print(user_choice)

main()
