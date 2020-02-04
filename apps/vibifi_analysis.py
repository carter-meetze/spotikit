import statistics
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import mpld3
import datetime

pop_playlist_avgs = {
    'valence': 0.48716,
    'energy': 0.56348,
    'danceability': 0.65572,
    'tempo': 121.80759
}


def get_ast_sign(birthday):

    day = int(birthday.split('-')[2])
    month = int(birthday.split('-')[1])

    if month == 12:
        astro_sign = 'sagittarius' if (day < 22) else 'capricorn'
    elif month == 1:
        astro_sign = 'capricorn' if (day < 20) else 'aquarius'
    elif month == 2:
        astro_sign = 'aquarius' if (day < 19) else 'pisces'
    elif month == 3:
        astro_sign = 'pisces' if (day < 21) else 'aries'
    elif month == 4:
        astro_sign = 'aries' if (day < 20) else 'taurus'
    elif month == 5:
        astro_sign = 'taurus' if (day < 21) else 'gemini'
    elif month == 6:
        astro_sign = 'gemini' if (day < 21) else 'cancer'
    elif month == 7:
        astro_sign = 'cancer' if (day < 23) else 'leo'
    elif month == 8:
        astro_sign = 'leo' if (day < 23) else 'virgo'
    elif month == 9:
        astro_sign = 'virgo' if (day < 23) else 'libra'
    elif month == 10:
        astro_sign = 'libra' if (day < 23) else 'scorpio'
    elif month == 11:
        astro_sign = 'scorpio' if (day < 22) else 'sagittarius'
    else:
        astro_sign = 'could not find it'

    return astro_sign


def get_ast_playlist(ast_sign):
    playlist_ids = {
        'sagittarius': '37i9dQZF1DX93MXPufCcuk',
        'capricorn': '37i9dQZF1DX2rcqmLx0nK4',
        'aquarius': '37i9dQZF1DX7F9VDRJOFhw',
        'pisces': '37i9dQZF1DWX0EDWtabVRv',
        'aries': '37i9dQZF1DX2DC3Q7JOmYe',
        'taurus': '37i9dQZF1DXbCgDGG5xQtb',
        'gemini': '37i9dQZF1DWWVULl5wUsL9',
        'cancer': '37i9dQZF1DXaeX3MJpiD4U',
        'leo': '37i9dQZF1DX7cvHpkIJFt2',
        'virgo': '37i9dQZF1DX6PdsVYbP4rI',
        'libra': '37i9dQZF1DXco4NYQOMLiT',
        'scorpio': '37i9dQZF1DX0YZgrwmizcR'
    }

    playlist_id = playlist_ids[ast_sign]

    return playlist_id


def mood_analyze(valence_mean, energy_mean, danceability_mean, tempo_mean):

    average_valence = 0.48716
    # original energy 0.68156, tweaked to give better results
    average_energy = 0.56348
    average_danceability = 0.65572
    average_tempo = 121.80759

    def diff_from_avg(input_average, playlist_average):
        pct_diff = ((input_average - playlist_average) / playlist_average)

        return pct_diff

    valence_diff = diff_from_avg(valence_mean, average_valence)
    energy_diff = diff_from_avg(energy_mean, average_energy)
    danceability_diff = diff_from_avg(danceability_mean, average_danceability)
    tempo_diff = diff_from_avg(tempo_mean, average_tempo)

    def mood_predict(input_average, playlist_average):
        threshold_low_factor = .3
        threshold_low = playlist_average - (playlist_average * threshold_low_factor)

        threshold_high_factor = .6
        threshold_high = playlist_average + (playlist_average * threshold_high_factor)

        if input_average >= threshold_high:
            mood = "high end"

        elif input_average < threshold_low:
            mood = "low end"

        elif input_average >= playlist_average and input_average < threshold_high:
            mood = "normal-high"

        elif input_average <= playlist_average and input_average > threshold_low:
            mood = "normal-low"

        else:
            mood = "normal"

        return mood

    valence_analysis = mood_predict(valence_mean, average_valence)
    energy_analysis = mood_predict(energy_mean, average_energy)
    danceability_analysis = mood_predict(danceability_mean, average_danceability)
    tempo_analysis = mood_predict(tempo_mean, average_tempo)

    return {'valence': valence_analysis, 'energy': energy_analysis, 'danceability': danceability_analysis, 'tempo': tempo_analysis}


def text_recommendation(vibe_index):

    vibe_index = int(vibe_index)

    if vibe_index <= 4:
        recommendation = 'your vibes are not so hot right now, make a playlist to make them better!'

    elif vibe_index > 4 and vibe_index <= 7:
        recommendation = 'your vibes are alright, making a playlist will help them out'

    elif vibe_index >= 8 and vibe_index <= 10:
        recommendation = 'your vibes are awesome, make a playlist to help keep them that way'

    elif vibe_index > 10:
        recommendation = 'wow you are really vibing'

    else:
        recommendation = 'something went wrong here, we cannot get your vibes'

    return recommendation


def vibe_chart(vibes_index):

    names = ['']
    values = [vibes_index]
    n = len(names)
    gradient = np.linspace(0, 1, 100).reshape(1, -1)
    plt.imshow(gradient, extent=[-0.25, 12.25, -1, n], aspect='auto', cmap='magma_r')
    sns.stripplot(x=values, y=names, color='white', size=12, edgecolor='white')
    plt.hlines(np.arange(0, n), -0.25, 12.25, linestyles='--', linewidth=1)
    plt.grid(False)
    plt.xlim(-0.25, 12.25)
    plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    fig = plt.figure()

    html = mpld3.fig_to_html(fig)

    return html

