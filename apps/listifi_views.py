from django.shortcuts import render
import requests
from django.views import View
from .listifi_forms import EntryForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import random
import os
from decouple import config


def login_render(request):
    template = loader.get_template("listifi_login.html")
    return HttpResponse(template.render)


class LAuthUser(View):

    def __init__(self):
        self.token = ""
        self.code = ""

    def get(self, request):
        return self.entryform(request)

    def entryform(self, request):

            if request.method == 'GET' and request.path == '/spotikit/apps/listifi/listifi_entry.html':
                try:

                    # flush all past sessions, just in case
                    if request.session.get('access_token'):
                        request.session.flush()
                    else:
                        pass

                    # get the authorization code, along with the access token
                    self.code = request.GET.get('code')
                    print("Retrieved code: " + self.code)
                    values = {'grant_type': 'authorization_code', 'code': self.code,
                              'redirect_uri':
                                  'http://localhost:8000/spotikit/apps/listifi/listifi_entry.html',
                              'client_id': os.environ['CLIENT_ID'],
                              'client_secret': os.environ['CLIENT_SECRET'],
                              'scope': ['playlist-modify-public', 'playlist-modify-private']}
                    auth = requests.post('https://accounts.spotify.com/api/token', data=values)
                    auth_data = auth.json()
                    print('access token is: ' + auth_data['access_token'])
                    self.token = auth_data['access_token']

                    # set the access token
                    request.session['access_token'] = self.token

                    print("current session: " + request.session.get('access_token'))
                    return HttpResponseRedirect(
                        'http://localhost:8000/spotikit/apps/listifi/listifi_entryform.html'
                    )

                except(KeyError, TypeError, NameError):
                    return HttpResponseRedirect('http://localhost:8000/spotify/listifi/listifi/listifi/listifi_error.html')

    form_class_entry = EntryForm
    template_name_entry = 'listifi_entryform.html'

    def post(self, request):

        # set the access token in this function
        if 'access_token' in request.session:
            self.token = request.session.get('access_token')
        else:
            return HttpResponseRedirect(
                'http://localhost:8000/spotify/listifi/listifi/listifi/listifi_error.html'
            )

        form = self.form_class_entry(request.POST)

        if request.method == 'POST' and request.path == '/spotikit/apps/listifi/listifi_result.html':
            if form.is_valid():
                artist_input = request.POST.get('artist')
                genre_input_list = request.POST.getlist('genre')
                genre_input = ','.join(genre_input_list)
                if request.POST.get('title'):
                    title_input = request.POST.get('title')
                else:
                    title_input = 'my ' + genre_input + " playlist"

                # get user id
                user_url = "https://api.spotify.com/v1/me"
                headers = {"Accept": "application/json", "Content-Type": "application/json",
                           "Authorization": "Bearer " + self.token}
                u = requests.get(user_url, headers=headers).json()

                # get artist from Spotify
                q = 'q=' + artist_input
                artist_url = "https://api.spotify.com/v1/search?" + q + "&type=artist"
                artist_call = requests.get(artist_url, headers=headers).json()

                # get genre from post data, determine artist input
                seed_genres = 'seed_genres=' + genre_input + '&'
                if artist_input:
                    seed_artists = "seed_artists=" + str(artist_call['artists']['items'][0]['id']) + "&"
                else:
                    seed_artists = ""

                # get the number of tracks
                if request.POST.get('tracks'):
                    number_of_tracks = 'limit=' + request.POST.get('tracks') + '&'
                else:
                    number_of_tracks = 'limit=10&'

                # recommendation parameters
                min_valence = 'min_valence=' + str(round(random.uniform(.25, .5), 1)) + "&"
                max_valence = 'max_valence=' + str(round(random.uniform(.71, 1), 1)) + "&"
                min_energy = 'min_energy=' + str(round(random.uniform(.3, .7), 1)) + "&"
                max_energy = 'max_energy=' + str(round(random.uniform(.71, 1), 1)) + "&"
                min_popularity = 'min_popularity=' + str(random.randint(15, 70))

                # get recommendations tracks
                url = "https://api.spotify.com/v1/recommendations?&market=US&" + \
                      number_of_tracks + \
                      seed_genres + \
                      seed_artists + \
                      min_valence + \
                      max_valence + \
                      min_energy + \
                      max_energy + \
                      min_popularity
                r = requests.get(url, headers=headers).json()
                tracks = []
                for t in r['tracks']:
                    tracks.append(t['uri'])
                json = {"name": title_input,
                        "description": "playlist brought to you by Listifi",
                        "public": "false"
                        }

                # test to see if it meets requested track number, tries it 4 times if it doesn't
                tracks_in_playlist = len(tracks)
                tries = 1
                while tries < 4 and tracks_in_playlist != number_of_tracks:
                    url = "https://api.spotify.com/v1/recommendations?&market=US&" + \
                          number_of_tracks + \
                          seed_genres + \
                          seed_artists + \
                          min_valence + \
                          max_valence + \
                          min_energy + \
                          max_energy + \
                          min_popularity
                    r = requests.get(url, headers=headers).json()
                    tracks = []
                    for t in r['tracks']:
                        tracks.append(t['uri'])
                    json = {"name": title_input,
                            "description": "playlist brought to you by Listifi",
                            "public": "false"
                            }
                    tries += 1

                if tries == 4:
                    url = "https://api.spotify.com/v1/recommendations?&market=US&" + \
                          number_of_tracks + \
                          seed_genres + \
                          seed_artists + \
                          min_valence + \
                          max_valence + \
                          min_energy + \
                          max_energy + \
                          min_popularity
                    r = requests.get(url, headers=headers).json()
                    tracks = []
                    for t in r['tracks']:
                        tracks.append(t['uri'])
                    json = {"name": title_input,
                            "description": "playlist brought to you by Listifi",
                            "public": "false"
                            }
                else:
                    pass

                print('times tried: ' + str(tries))

                # make a new playlist
                create_url = "https://api.spotify.com/v1/users/" + u['id'] + "/playlists"
                new_playlist = requests.post(create_url, headers=headers, json=json).json()
                open_url = new_playlist['external_urls']['spotify']

                # add the tracks to the playlist
                add_tracks_url = "https://api.spotify.com/v1/users/" + u['id'] + "/playlists/" + new_playlist[
                    'id'] + "/tracks" + "?uris=" + ",".join(tracks)
                add_tracks = requests.post(add_tracks_url, headers=headers).json()
                return render(request, 'listifi_result.html', {
                    'artist': form.cleaned_data['artist'],
                    'genre': form.cleaned_data['genre'],
                    'title': form.cleaned_data['title'],
                    'tracks': form.cleaned_data['tracks'],
                    'url': open_url
                })
            return render(request, self.template_name_entry, {'form': form})
