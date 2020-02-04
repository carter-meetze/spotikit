from django.shortcuts import render
import requests
from django.views import View
from .vibifi_forms import EntryForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import random
import os
from pprint import pprint as pprint
import statistics
from .vibifi_analysis import mood_analyze, text_recommendation, vibe_chart, get_ast_sign, get_ast_playlist
import datetime
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
from .vibifi_color_analysis import get_dominant_color_hex
from collections import Counter
from .vibifi_analysis import pop_playlist_avgs
from .vibifi_planet_colors import col_dif_scale
import mysql.connector
import webbrowser
matplotlib.use("Agg")


def login_render(request):
    template = loader.get_template("vibifi_login.html")
    return HttpResponse(template.render)


class VAuthUser(View):

    def __init__(self):
        self.token = ""
        self.code = ""
        self.valence_average = 0
        self.energy_average = 0
        self.danceability_average = 0
        self.sign = ""
        self.user_id = ""

    def get(self, request):
        return self.entryform(request)

    def entryform(self, request):

            if request.method == 'GET' and request.path == '/spotikit/apps/vibifi/vibifi_entry.html':
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
                                  'http://localhost:8000/spotikit/apps/vibifi/vibifi_entry.html',
                              'client_id': os.environ['CLIENT_ID'],
                              'client_secret': os.environ['CLIENT_SECRET'],
                              'scope': ['playlist-modify-public', 'playlist-modify-private', 'user-read-recently-played']}
                    auth = requests.post('https://accounts.spotify.com/api/token', data=values)
                    auth_data = auth.json()
                    print('access token is: ' + auth_data['access_token'])
                    self.token = auth_data['access_token']

                    # set the access token
                    request.session['access_token'] = self.token

                    # mysql info
                    mydb = mysql.connector.connect(
                        host="127.0.0.1",
                        user="root",
                        passwd="btbam1207",
                        database="sys",
                        auth_plugin="mysql_native_password"
                    )
                    mycursor = mydb.cursor()

                    headers = {"Accept": "application/json", "Content-Type": "application/json",
                               "Authorization": "Bearer " + self.token}

                    user_url = 'https://api.spotify.com/v1/me'
                    user_id_json = requests.get(user_url, headers=headers).json()
                    self.user_id = user_id_json['id']
                    print(self.user_id)

                    query = "SELECT * FROM sys.astrolifi WHERE user_name = %s"
                    val = (str(self.user_id), )
                    mycursor.execute(query, val)
                    myresult = mycursor.fetchall()

                    for x in myresult:
                        print(x)

                    if myresult:
                        show_birthday = 'true'
                    else:
                        show_birthday = 'false'

                    print("current session: " + request.session.get('access_token'))
                    return HttpResponseRedirect(
                        'http://localhost:8000/spotikit/apps/vibifi/vibifi_entryform.html'
                    )

                except(KeyError, TypeError, NameError):
                    return HttpResponseRedirect('http://localhost:8000/astrolifi/vibifi/vibifi/listifi/listifi_error.html')

    form_class_entry = EntryForm
    template_name_entry = 'listifi_entryform.html'

    def post(self, request):

        # mysql info
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd="btbam1207",
            database="sys",
            auth_plugin="mysql_native_password"
        )
        mycursor = mydb.cursor()

        # set the access token in this function
        if 'access_token' in request.session:
            self.token = request.session.get('access_token')
        else:
            return HttpResponseRedirect(
                'http://localhost:8000/astrolifi/vibifi/vibifi/listifi/listifi_error.html'
            )

        form = self.form_class_entry(request.POST)

        if request.path == '/astrolifi/vibifi/vibifi/listifi/listifi_login.html':
            return HttpResponseRedirect('https://www.spotify.com/logout/')

        if request.method == 'POST' and request.path == '/spotikit/apps/vibifi/vibifi_data.html':

            if form.is_valid():

                birthday_month = request.POST.get('birthday_month')
                birthday_day = request.POST.get('birthday_day')
                birthday_year = request.POST.get('birthday_year')

                birthday = birthday_year + '-' + birthday_month + '-' + birthday_day
                print(birthday)
                sql_bday = str(birthday_year) + '/' + str(birthday_month) + '/' + str(birthday_day)

                headers = {"Accept": "application/json", "Content-Type": "application/json",
                           "Authorization": "Bearer " + self.token}

                user_url = 'https://api.spotify.com/v1/me'
                user_id_json = requests.get(user_url, headers=headers).json()
                self.user_id = user_id_json['id']
                print(self.user_id)

                sign = get_ast_sign(birthday)
                self.sign = get_ast_sign(birthday)

                sign_playlist_id = get_ast_playlist(sign)

                sign_playlist_url = 'https://api.spotify.com/v1/playlists/' + sign_playlist_id + '/tracks'

                sign_playlist_data = requests.get(sign_playlist_url, headers=headers).json()

                sign_playlist_image_data = requests.get('https://api.spotify.com/v1/playlists/' + sign_playlist_id, headers=headers).json()

                sign_playlist_image = sign_playlist_image_data['images'][0]['url']

                sign_track_ids = []
                for item in sign_playlist_data['items']:
                    sign_track_ids.append(item['track']['id'])

                sign_tracks_url = "https://api.spotify.com/v1/audio-features?ids=" + '%2C'.join([x for x in sign_track_ids])
                sign_tracks_analysis = requests.get(sign_tracks_url, headers=headers).json()

                sign_valence = []
                for item in sign_tracks_analysis['audio_features']:
                    sign_valence.append(item['valence'])

                sign_energy = []
                for item in sign_tracks_analysis['audio_features']:
                    sign_energy.append(item['energy'])

                sign_danceability = []
                for item in sign_tracks_analysis['audio_features']:
                    sign_danceability.append(item['danceability'])

                sign_tempo = []
                for item in sign_tracks_analysis['audio_features']:
                    sign_tempo.append(item['tempo'])

                sign_valence_average = statistics.mean(sign_valence)
                sign_energy_average = statistics.mean(sign_energy)
                sign_danceability_average = statistics.mean(sign_danceability)
                sign_tempo_average = statistics.mean(sign_tempo)

                user_url = "https://api.spotify.com/v1/me/player/recently-played?type=track&limit=50"

                tracks = requests.get(user_url, headers=headers).json()

                img_urls = []

                id_list = []

                for track in tracks['items']:
                    track_id_list = []
                    track_id_list.append(track['played_at'])
                    track_id_list.append(track['track']['name'])
                    track_id_list.append(track['track']['id'])
                    img_urls.append(track['track']['album']['images'][1]['url'])
                    id_list.append(track_id_list)

                dominant_color_hex = get_dominant_color_hex(img_urls)
                dominant_rbg = dominant_color_hex.lstrip('#')
                d_rgb = list(int(dominant_rbg[i:i+2], 16) for i in (0, 2, 4))

                tracks_url = "https://api.spotify.com/v1/audio-features?ids=" + '%2C'.join([x[2] for x in id_list])
                analysis = requests.get(tracks_url, headers=headers).json()


                # for item in analysis["audio_features"]:
                #     if item is None:
                #         pass
                #     else:
                #         valence_recent.append(item["valence"])

                valence_recent = []
                energy_recent = []
                danceability_recent = []
                tempo_recent = []
                x = 0
                while x < len(analysis["audio_features"]):
                    if analysis["audio_features"][x] is None:
                        id_list.pop(x)
                    else:
                        valence_recent.append(analysis["audio_features"][x]["valence"])
                        energy_recent.append(analysis["audio_features"][x]["valence"])
                        danceability_recent.append(analysis["audio_features"][x]["valence"])
                        tempo_recent.append(analysis["audio_features"][x]["valence"])
                    x += 1


                # for item in analysis['audio_features']:
                #     if item is None:
                #         pass
                #     else:
                #         energy_recent.append(item['energy'])
                #
                # danceability_recent = []
                # for item in analysis['audio_features']:
                #     if item is None:
                #         pass
                #     else:
                #         danceability_recent.append(item['danceability'])
                #
                # tempo_recent = []
                # for item in analysis['audio_features']:
                #     if item is None:
                #         pass
                #     else:
                #         tempo_recent.append(item['tempo'])

                i = 0
                while i < len(id_list):
                    id_list[i].append(valence_recent[i])
                    i += 1

                i = 0
                while i < len(id_list):
                    id_list[i].append(energy_recent[i])
                    i += 1

                i = 0
                while i < len(id_list):
                    id_list[i].append(danceability_recent[i])
                    i += 1

                i = 0
                while i < len(id_list):
                    id_list[i].append(tempo_recent[i])
                    i += 1

                average_valence = statistics.mean(valence_recent)
                self.valence_average = statistics.mean(valence_recent)
                average_danceability = statistics.mean(danceability_recent)
                self.danceability_average = statistics.mean(danceability_recent)
                average_energy = statistics.mean(energy_recent)
                self.energy_average = statistics.mean(energy_recent)
                average_tempo = statistics.mean(tempo_recent)

                mood_prediction = mood_analyze(average_valence, average_energy, average_danceability, average_tempo)

                sign_mood_prediction = mood_analyze(sign_valence_average, sign_energy_average, sign_danceability_average, sign_tempo_average)

                def vibes_index(mood_prediction):

                    valence_vibe = mood_prediction['valence']
                    energy_vibe = mood_prediction['energy']
                    danceability_vibe = mood_prediction['danceability']
                    tempo_vibe = mood_prediction['tempo']

                    def analysis_to_number(attribute_analysis):

                        if attribute_analysis == 'low end':
                            number = 1

                        elif attribute_analysis == 'normal-low':
                            number = 2

                        elif attribute_analysis == 'normal-high':
                            number = 3

                        elif attribute_analysis == 'high end':
                            number = 4

                        else:
                            number = 0

                        return number

                    valence_number = analysis_to_number(valence_vibe)
                    energy_number = analysis_to_number(energy_vibe)
                    danceability_number = analysis_to_number(danceability_vibe)
                    tempo_number = analysis_to_number(tempo_vibe)

                    vibes_number = valence_number + energy_number + danceability_number + tempo_number

                    return {'vibes_number': vibes_number, 'valence_number': valence_number, 'energy_number': energy_number, 'danceability_number': danceability_number, 'tempo_number': tempo_number}

                overall_vibes_number = vibes_index(mood_prediction)['vibes_number']

                # +6 / 2 to simulate the dominant color effects, update later
                sign_vibes_number = (vibes_index(sign_mood_prediction)['vibes_number'] + 6) / 2

                color_vibes_number = col_dif_scale(sign, d_rgb)

                print(overall_vibes_number)
                print(sign_vibes_number)
                print(color_vibes_number)

                vibes_number = round(((overall_vibes_number + sign_vibes_number + color_vibes_number) / 3) * 2) / 2

                recommendation = text_recommendation(vibes_number)

                # sql for average valence
                mycursor.execute("SELECT AVG(valence) FROM sys.astrolifi WHERE user_name = " + str(self.user_id))
                historical_valence = mycursor.fetchall()[0][0]
                mycursor.execute("SELECT AVG(energy) FROM sys.astrolifi WHERE user_name = " + str(self.user_id))
                historical_energy = mycursor.fetchall()[0][0]
                mycursor.execute("SELECT AVG(danceability) FROM sys.astrolifi WHERE user_name = " + str(self.user_id))
                historical_danceability = mycursor.fetchall()[0][0]
                mycursor.execute("SELECT AVG(tempo) FROM sys.astrolifi WHERE user_name = " + str(self.user_id))
                historical_tempo = mycursor.fetchall()[0][0]

                # for dominant color
                plt.figure(figsize=(1, .5))
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0, facecolor=dominant_color_hex)
                image_base64_color = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
                buf.close()

                # for main chart
                plt.figure(figsize=(10, 1))
                names = ['']
                n = len(names)
                gradient = np.linspace(0, 1, 100).reshape(1, -1)
                plt.imshow(gradient, extent=[-0.25, 12.25, -1, n], aspect='auto', cmap='magma')
                my_vibe = plt.vlines(vibes_number, -1, 1, linestyles='-', linewidth=5, colors=dominant_color_hex)
                avg_vibe = plt.vlines(sign_vibes_number, -1, 1, linestyles='-', linewidth=3, colors='#e3e4df')
                plt.grid(False)
                plt.xlim(-0.25, 12.25)
                plt.axis('off')
                plt.legend([my_vibe, avg_vibe], ['your vibe', 'your average vibe'], loc='best')

                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
                image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
                buf.close()

                # for valence
                plt.figure(figsize=(10, .5))
                names = ['']
                n = len(names)
                gradient = np.linspace(0, 1, 100).reshape(1, -1)
                plt.imshow(gradient, extent=[-0.25, 1.25, -1, n], aspect='auto', cmap='magma')
                plt.vlines(average_valence, -1, 1, linestyles='-', linewidth=5, colors=dominant_color_hex)
                plt.vlines(historical_valence, -1, 1, linestyles='-', linewidth=3, colors='#e3e4df')
                plt.grid(False)
                plt.xlim(-0.25, 1.25)
                plt.axis('off')

                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
                image_base64_valence = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
                buf.close()

                # for energy
                plt.figure(figsize=(10, .5))
                names = ['']
                n = len(names)
                gradient = np.linspace(0, 1, 100).reshape(1, -1)
                plt.imshow(gradient, extent=[-0.25, 1.25, -1, n], aspect='auto', cmap='magma')
                plt.vlines(average_energy, -1, 1, linestyles='-', linewidth=5, colors=dominant_color_hex)
                plt.vlines(historical_energy, -1, 1, linestyles='-', linewidth=3, colors='#e3e4df')
                plt.grid(False)
                plt.xlim(-0.25, 1.25)
                plt.axis('off')

                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
                image_base64_energy = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
                buf.close()

                # for danceability
                plt.figure(figsize=(10, .5))
                names = ['']
                n = len(names)
                gradient = np.linspace(0, 1, 100).reshape(1, -1)
                plt.imshow(gradient, extent=[-0.25, 1.25, -1, n], aspect='auto', cmap='magma')
                plt.vlines(average_danceability, -1, 1, linestyles='-', linewidth=5, colors=dominant_color_hex)
                plt.vlines(historical_danceability, -1, 1, linestyles='-', linewidth=3, colors='#e3e4df')
                plt.grid(False)
                plt.xlim(-0.25, 1.25)
                plt.axis('off')

                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
                image_base64_danceability = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
                buf.close()

                # for tempo
                plt.figure(figsize=(10, .5))
                names = ['']
                n = len(names)
                gradient = np.linspace(0, 1, 100).reshape(1, -1)
                plt.imshow(gradient, extent=[-100.25, 150.25, -1, n], aspect='auto', cmap='magma')
                plt.vlines(average_tempo, -1, 1, linestyles='-', linewidth=5, colors=dominant_color_hex)
                plt.vlines(historical_tempo, -1, 1, linestyles='-', linewidth=3, colors='#e3e4df')
                plt.grid(False)
                plt.xlim(-100.25, 150.25)
                plt.axis('off')

                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
                image_base64_tempo = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
                buf.close()

                # time to insert everything into the database

                sql = "INSERT INTO sys.astrolifi VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (
                    str(self.token),
                    str(self.user_id),
                    datetime.date.today(),
                    sql_bday,
                    average_valence,
                    average_energy,
                    average_danceability,
                    average_tempo,
                    d_rgb[0],
                    d_rgb[1],
                    d_rgb[2]
                )
                pprint(val)

                mycursor.execute(sql, val)

                mydb.commit()
                print(mycursor.rowcount, "record inserted.")

                mycursor.execute("SELECT MAX(date) FROM sys.astrolifi")
                date = mycursor.fetchall()[0][0]

                return render(request, 'vibifi_data.html', {
                    'vibe': vibes_number,
                    'recommendation': recommendation,
                    'sign': str.title(sign),
                    'sign_vibe': sign_vibes_number,
                    'sign_img': sign_playlist_image,
                    'image': image_base64,
                    'valence': vibes_index(mood_prediction)['valence_number'],
                    'image_valence': image_base64_valence,
                    'energy': vibes_index(mood_prediction)['energy_number'],
                    'image_energy': image_base64_energy,
                    'danceability': vibes_index(mood_prediction)['danceability_number'],
                    'image_danceability': image_base64_danceability,
                    'tempo': vibes_index(mood_prediction)['tempo_number'],
                    'image_tempo': image_base64_tempo,
                    'image_color': image_base64_color,
                    'date': date,
                    'mood_hex': dominant_color_hex
                }
                              )

            else:
                pass

        if request.method == 'POST' and request.path == '/spotikit/apps/vibifi/vibifi_playlist.html':

            get_artists_url = 'https://api.spotify.com/v1/me/top/artists?time_range=medium_term&limit=10'
            headers = {"Accept": "application/json", "Content-Type": "application/json",
                       "Authorization": "Bearer " + self.token}

            top_artists_json = requests.get(get_artists_url, headers=headers).json()

            top_genres_sublist = []
            i = 0
            while i < len(top_artists_json['items']):
                for x in top_artists_json['items'][i]['genres']:
                    top_genres_sublist.append(x)
                i += 1

            top_artists_sublist = []
            i = 0
            while i < len(top_artists_json['items']):
                top_artists_sublist.append(top_artists_json['items'][i]['id'])
                i += 1
            top_artists = random.choices(top_artists_sublist, k=2)
            top_genres = random.choices(Counter(top_genres_sublist).most_common(6), k=2)
            first_genre = top_genres[0][0]
            second_genre = top_genres[1][0]

            rec_url = 'https://api.spotify.com/v1/recommendations?'
            tracks = 15
            market = 'US'
            seed_artists_playlist = ','.join(top_artists)
            seed_genres_playlist = ','.join([first_genre, second_genre])

            if self.energy_average < pop_playlist_avgs['energy']:
                energy = '&min_energy=' + str(pop_playlist_avgs['energy'])
            else:
                energy = ''
            if self.valence_average < pop_playlist_avgs['valence']:
                valence = '&min_valence=' + str(pop_playlist_avgs['valence'])
            else:
                valence = ''
            if self.danceability_average < pop_playlist_avgs['danceability']:
                danceability = '&min_danceability=' + str(pop_playlist_avgs['danceability'])
            else:
                danceability = ''

            playlist_rec = requests.get(rec_url + 'limit=' + str(tracks) + '&market=' + market + '&seed_artists=' + seed_artists_playlist + '&seed_genres=' + seed_genres_playlist + energy + valence + danceability, headers=headers).json()
            pprint(playlist_rec)
            tracks = []
            t = 0
            while t < len(playlist_rec['tracks']):
                tracks.append(playlist_rec['tracks'][t]['uri'])
                t += 1

            json = {
                "name": "Vibifi Playlist",
                "description": "",
                "public": "false"
                    }

            user_url = 'https://api.spotify.com/v1/me'
            user_id_json = requests.get(user_url, headers=headers).json()
            user_id = user_id_json['id']

            new_playlist = requests.post('https://api.spotify.com/v1/users/' + user_id + '/playlists/', headers=headers, json=json).json()
            open_url = new_playlist['external_urls']['spotify']

            playlist_id = new_playlist['id']
            add_tracks_url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks?uris=' + ','.join(tracks)

            add_tracks = requests.post(add_tracks_url, headers=headers).json()

            return render(request, 'vibifi_playlist.html', {
                'url': open_url
            })

        else:
            pass
