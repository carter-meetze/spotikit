
planet_colors = {
    'aries': {
        'planet': 'mars',
        'rgb': [231, 125, 17]
    },
    'taurus': {
        'planet': 'venus',
        'rgb': [249, 194, 26]
    },
    'gemini': {
        'planet': 'mercury',
        'rgb': [231, 232, 236]
    },
    'cancer': {
        'planet': 'moon',
        'rgb': [201, 201, 201]
    },
    'leo': {
        'planet': 'sun',
        'rgb': [242, 197, 89]
    },
    'virgo': {
        'planet': 'mercury',
        'rgb': [177, 173, 173]
    },
    'libra': {
        'planet': 'venus',
        'rgb': [227, 158, 28]
    },
    'scorpio': {
        'planet': 'mars',
        'rgb': [253, 166, 0]
    },
    'sagittarius': {
        'planet': 'jupiter',
        'rgb': [235, 243, 246]
    },
    'capricorn': {
        'planet': 'saturn',
        'rgb': [227, 224, 192]
    },
    'aquarius': {
        'planet': 'saturn',
        'rgb': [191, 189, 175]
    },
    'pisces': {
        'planet': 'jupiter',
        'rgb': [216, 202, 157]
    }

}

color_scale = {
    'low end': {
        'criteria': [1, 74.1],
        'score': 12
    },
    'normal-low': {
        'criteria': [74.2, 220.3],
        'score': 9
    },
    'normal-high': {
        'criteria': [220.4, 439.6],
        'score': 6
    },
    'high end': {
        'criteria': [439.7, 732],
        'score': 3
    }

}


def col_dif_scale(sign, rgb):

    dif_list = []
    i = 0

    while i < 3:
        dif_list.append(abs(planet_colors[sign]['rgb'][i] - rgb[i]))
        i += 1
    dif = sum(dif_list)

    score = []
    j = 0

    while j < 4:
        if dif >= color_scale[list(color_scale.keys())[j]]['criteria'][0] and color_scale[list(color_scale.keys())[j]]['criteria'][1]:
            score.append(color_scale[list(color_scale.keys())[j]]['score'])
        j += 1
    else:
        j += 1

    return score[-1]


