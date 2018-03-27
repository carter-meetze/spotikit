import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

# get the username from terminal
username = sys.argv[1]

# User ID: spotify:user:1243461497

# erase cache and prompt for user permission
try:
    token = util.prompt_for_user_token(username)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username)

# create spotify object
spotifyObject = spotipy.Spotify(auth=token)

user = spotifyObject.current_user()

displayName = user['display_name']
followers = user['followers']['total']

while True:

    print()
    print(">>> Welcome to Spotipy " + displayName + "!")
    print(">>> You have " + str(followers) + " followers")
    print()
    print("0 - Search for an artist")
    print("1 - exit")
    print()
    choice = input("Your choice: ")

    if choice == "0":
        print("0")
        searchQuery = input("Ok bro, what's their name?: ")
        print()

        searchResults = spotifyObject.search(searchQuery, 1, 0, "artist")
        print(json.dumps(searchResults, sort_keys=True, indent=4))

        # artist details
        artist = searchResults['artists']['items'][0]
        print(artist['name'])
        print(artist['genres'][0])
        print()
        webbrowser.open(artist['images'][0]['url'])
        artistID = artist['id']

        # album details
        trackURIs = []
        trackArt = []
        z = 0

        # extract album data
        albumResults = spotifyObject.artist_albums(artistID)
        albumResults = albumResults['items']

        for item in albumResults:
            print("ALBUM " + item['name'])
            albumID = item['id']
            albumArt = item['images'][0]['url']

            # extract track data
            trackResults = spotifyObject.album_tracks(albumID)
            trackResults = trackResults['items']

            for item in trackResults:
                print(str(z) + ": " + item['name'])
                trackURIs.append(item['uri'])
                trackArt.append(albumArt)
                z += 1
            print()
        # see album artist
        while True:
            songSelection = input("Enter a song number to see the album art")
            if songSelection == "x":
                break
            webbrowser.open(trackArt[int(songSelection)])

    if choice == "1":
        break

# print(json.dumps(VARIABLE, sort_keys=True, indent=4))
