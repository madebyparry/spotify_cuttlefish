#!/usr/bin/env python3
import sys,os
import curses
import cuttlefish
import time
import catimage


catimg = catimage


def draw_menu(stdscr):
    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while (True):

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            cuttlefish.playPauseMusic()
        elif k == curses.KEY_UP:
            cuttlefish.like_song()
        elif k == curses.KEY_SRIGHT:
            cuttlefish.nextTrack()
        elif k == curses.KEY_SLEFT:
            cuttlefish.prevTrack()

        if k == ord('q'):
            break
        
        cursor_x = max(0, cursor_x)
        cursor_x = min(width-1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height-1, cursor_y)

        # get spotify values
        current_runtime = cuttlefish.printCurrentRuntime()
        currently_playing = cuttlefish.currentlyPlaying()
        stored_track = ''

#        song_duration = {
#                'minutes_elapsed' : ,
#                'seconds_elapsed' : ,
#                'minutes_remaining' : ,
#                'seconds_remaining' : ,
#                }
#        song_info = {
#                'artist_name' : ,
#                'song_name' : ,
#                'album_art' : ,
#                'album_name' : ,
#                }
        # Declaration of strings
        keystr = "Spotify Cuttlefish Player"[:width-1]
        subtitle = "{}".format(currently_playing['album_name'])[:width-1]
        title = "{} - {}".format(currently_playing['track_name'], currently_playing['artist_name'])[:width-1]
        statusbarstr = " 0.0.1 | SPOTIFY CUTTLEFISH PLAYER | {}".format(current_runtime)
        album_art = currently_playing['album_art']

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((height // 2) - 2)
        start_album_art_x = 2
        start_album_art_y = 2

        # make windows
        album_window = curses.newwin((height - 4), ((height - 4) * 2), start_album_art_y, start_album_art_x)
        info_window = curses.newwin(8, round(width / 2))
        # album_window = curses.newpad(50, 50) #, start_album_art_y, start_album_art_x)
        album_window.border()
        #playing_window = curses.newwin()
        rendered_album_art = cuttlefish.displayCatImg(currently_playing['album_art'], 10)
        rendered_album_art = catimage.generateGreyscale('/home/nicholas/spotify_cuttlefish/data/album_art_cache', (round(height * 2) - 9))
        album_window.addstr(rendered_album_art)
        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, ((width // 2) + width // 4), title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y + 1, ((width // 2) + width // 4), subtitle)
        stdscr.addstr(start_y + 3, ((width // 2) + width // 4), '-' * 4)
        stdscr.addstr(start_y + 5, ((width // 2) + width // 4), keystr)
        stdscr.move(cursor_y, cursor_x)

        stdscr.nodelay(True)
        # Refresh the screen
        time.sleep(1)
        k = stdscr.getch()
        stdscr.refresh()
        if stored_track != currently_playing['track_name']:
            stored_track = currently_playing['track_name']
            album_window.refresh()
            # album_window.refresh(0,0,2,2,50,50)
        # Wait for next input


def main():
    cuttlefish.setEnvVars()
    #cuttlefish.authenticateSpotipyOauth()
    #cuttlefish.authenticateSpotipyCreds()
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
