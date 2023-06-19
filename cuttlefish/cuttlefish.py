#!/usr/bin/env python3

import spotipy
import sys
import inquirer
from time import sleep
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

def main():
    initialSelection = [
    inquirer.List('initial_selection',
                    message="Cuttlefish options:",
                    choices=[
                        'next track',
                        'currently playing',
                        'display on pi',
                        'play music',
                        'pause music',
                        'related artists',
                        'user top tracks', 
                        'user playlists', 
                        'gen test oauth'
                        ],
                ),
    ]
    userSelect = inquirer.prompt(initialSelection)
    triageSelection(userSelect["initial_selection"])

def authenticateSpotipyCreds():
    global sp
    global sessionUser
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    sessionUser = '73e213ujw0wxcy49bxwcfuhik'

def authenticateSpotipyOauth(scope):
    global sp
    global sessionUser
    auth_manager = SpotifyClientCredentials()
    # sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,open_browser=False))
    sessionUser = '73e213ujw0wxcy49bxwcfuhik'

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
        
def userTopTracks():
    print("top tracks")
    authenticateSpotipyOauth("user-top-read")
    # scope = 'user-top-read'
    ranges = ['short_term', 'medium_term', 'long_term']
    for sp_range in ['short_term', 'medium_term', 'long_term']:
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

def currentlyPlaying():
    print("currently playing: \n")
    authenticateSpotipyOauth('user-read-currently-playing')
    track = sp.current_user_playing_track()
    if not track is None:
        print(track['item']['album']['images'][0]['url'])
        print(track['item']['artists'][0]['name'])
        print(track['item']['album']['name'])
        print(track['item']['name'])
    else:
        print("No track currently playing.") 

def playMusic():
    authenticateSpotipyOauth('user-read-playback-state,user-modify-playback-state')
    sp.start_playback()

def pauseMusic():
    authenticateSpotipyOauth('user-modify-playback-state')
    sp.pause_playback()

def nextTrack():
	authenticateSpotipyOauth('user-modify-playback-state')
	sp.next_track()
        
def genTestOauth():
    authenticateSpotipyOauth('user-read-playback-state,user-modify-playback-state,user-read-currently-playing,user-top-read')
    displayCuttlefish()
    print(".cache generated")
    sp.volume(100)
    sleep(2)
    sp.volume(50)
    sleep(2)
    sp.volume(100)


def displayCuttlefish():
    pi_name = "192.168.0.201"
    print(pi_name)
    print(sp.devices())


def triageSelection(user_choice):
    if user_choice == 'related artists':
        relatedArtists()
    elif user_choice == 'user top tracks':
        userTopTracks()
    elif user_choice == 'user playlists':
        listUserPlaylists()
    elif user_choice == 'currently playing':
        currentlyPlaying()
    elif user_choice == 'play music':
        playMusic()
    elif user_choice == 'display on pi':
        displayCuttlefish()
    elif user_choice == 'next track':
        nextTrack()
    elif user_choice == 'gen test oauth':
        genTestOauth()
    elif user_choice == 'pause music':
        pauseMusic()
    else:
        print(user_choice)

main()
