import requests
import pprint
import re
import json
import random



# GET response from spotify to get User's ID
user_url = "https://api.spotify.com/v1/me"
headers = {"Accept": "application/json", "Content-Type": "application/json",
           "Authorization": "Bearer BQDsolUBIEW_PV6ugS9wwLfg6Z8UU35YwN9FuJO0_5YdUJFDCgmbL5BFYFtKNKa7k-wJh7NBaRff-MKdeyOcqDH_2_8wRWaOjZI7231An9jA4nJKo9tpnKlHR8ePbnB_VRjG2RLHmMIzWTaSGIM6vfz8nIPERD3B1o-ntPTx6ZQ0FvdWsOuqu22-3Y3LMKtIDUducdj5mlgIprc"}

u = requests.get(user_url, headers=headers).json()

print(u['id'])

# get an artist's id

# first the artist is inputted
artist_input = 'Yellow Claw'

q = 'q=' + artist_input

artist_url = "https://api.spotify.com/v1/search?" + q + "&type=artist"

artist_call = requests.get(artist_url, headers=headers).json()

# next we'll get genres

genre_input = 'edm'

# put everything together as a GET response from spotify to provide recommendations

seed_genres = 'seed_genres=' + genre_input + '&'
if artist_input:
    seed_artists = "seed_artists=" + str(artist_call['artists']['items'][0]['id']) + "&"
else:
    seed_artists = ""
min_valence = 'min_valence=' + str(round(random.uniform(.4, .6), 1)) + "&"
max_valence = 'max_valence=' + str(round(random.uniform(.61, 1), 1)) + "&"
min_energy = 'min_energy=' + str(round(random.uniform(.3, .6), 1)) + "&"
max_energy = 'max_energy=' + str(round(random.uniform(.61, 1), 1)) + "&"
min_popularity = 'min_popularity=' + str(random.randint(15, 70))

url = "https://api.spotify.com/v1/recommendations?limit=10&market=US&" + seed_genres + seed_artists + min_valence + max_valence + min_energy + max_energy + min_popularity


r = requests.get(url, headers=headers).json()
print(r)


# extract all of the track IDs from the GET response
# result = re.findall("spotify:track:.*$", r.text, re.MULTILINE)


tracks = []
for t in r['tracks']:
    tracks.append(t['uri'])



json = {"name": "Carter's " + genre_input + " playlist",
        "description": "description",
        "public": "false"
        }

create_url = "https://api.spotify.com/v1/users/" + u['id'] + "/playlists"

new_playlist = requests.post(create_url, headers=headers, json=json).json()

print(new_playlist['id'])
print(new_playlist)

# add the tracks to the playlist

add_tracks_url = "https://api.spotify.com/v1/users/" + u['id'] + "/playlists/" + new_playlist['id'] + "/tracks" + "?uris=" + ",".join(tracks)

add_tracks = requests.post(add_tracks_url, headers=headers).json()

print(add_tracks)





'''
Available Genres
    "acoustic",
    "afrobeat",
    "alt-rock",
    "alternative",
    "ambient",
    "anime",
    "black-metal",
    "bluegrass",
    "blues",
    "bossanova",
    "brazil",
    "breakbeat",
    "british",
    "cantopop",
    "chicago-house",
    "children",
    "chill",
    "classical",
    "club",
    "comedy",
    "country",
    "dance",
    "dancehall",
    "death-metal",
    "deep-house",
    "detroit-techno",
    "disco",
    "disney",
    "drum-and-bass",
    "dub",
    "dubstep",
    "edm",
    "electro",
    "electronic",
    "emo",
    "folk",
    "forro",
    "french",
    "funk",
    "garage",
    "german",
    "gospel",
    "goth",
    "grindcore",
    "groove",
    "grunge",
    "guitar",
    "happy",
    "hard-rock",
    "hardcore",
    "hardstyle",
    "heavy-metal",
    "hip-hop",
    "holidays",
    "honky-tonk",
    "house",
    "idm",
    "indian",
    "indie",
    "indie-pop",
    "industrial",
    "iranian",
    "j-dance",
    "j-idol",
    "j-pop",
    "j-rock",
    "jazz",
    "k-pop",
    "kids",
    "latin",
    "latino",
    "malay",
    "mandopop",
    "metal",
    "metal-misc",
    "metalcore",
    "minimal-techno",
    "movies",
    "mpb",
    "new-age",
    "new-release",
    "opera",
    "pagode",
    "party",
    "philippines-opm",
    "piano",
    "pop",
    "pop-film",
    "post-dubstep",
    "power-pop",
    "progressive-house",
    "psych-rock",
    "punk",
    "punk-rock",
    "r-n-b",
    "rainy-day",
    "reggae",
    "reggaeton",
    "road-trip",
    "rock",
    "rock-n-roll",
    "rockabilly",
    "romance",
    "sad",
    "salsa",
    "samba",
    "sertanejo",
    "show-tunes",
    "singer-songwriter",
    "ska",
    "sleep",
    "songwriter",
    "soul",
    "soundtracks",
    "spanish",
    "study",
    "summer",
    "swedish",
    "synth-pop",
    "tango",
    "techno",
    "trance",
    "trip-hop",
    "turkish",
    "work-out",
    "world-music"
'''