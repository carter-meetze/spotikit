import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util

username = sys.argv[1]

# my user id is 1243461497
try:
    token = util.prompt_for_user_token(username)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username)

# create spotify object
spotifyObject = spotipy.Spotify(auth=token)

user = spotifyObject.current_user()

while True:

    print()
    print("Welcome to the playlist maker!")
    print("Enter some options below:")
    print()
    artistSearch = input("enter an artist name here: ")
    artistResults = spotifyObject.search(artistSearch, 1, 0, "artist")
    artist = artistResults['artists']['items'][0]
    artistID = artist['id']

    print(artistID)

    show_recommendations = spotifyObject.recommendations(seed_artists='69GGBxA162lTqCwzJG5jLp')
    print(show_recommendations)
