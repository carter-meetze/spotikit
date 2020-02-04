from PIL import Image
import urllib.request
from io import BytesIO
import statistics
from collections import Counter


def get_dominant_color_hex(url_list):

    def get_img(url):
        file = BytesIO(urllib.request.urlopen(url).read())
        img = Image.open(file)
        return img

    def stitch_img(url_list):
        images = [get_img(x) for x in url_list]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset,0))
            x_offset += im.size[0]
        return new_im

    stitch = stitch_img(url_list).getcolors(maxcolors=10000000)
    top_colors = sorted(stitch, key=lambda x: x[0], reverse=True)[:15]
    values = [x[1] for x in top_colors if statistics.mean(Counter(x[1]).values()) == 1]

    rgb = values[:3]

    j = 0
    r = []
    g = []
    b = []
    while j < len(rgb):
        r.append(rgb[j][0])
        g.append(rgb[j][1])
        b.append(rgb[j][2])
        j += 1

    r_avg = round(statistics.mean(r))
    g_avg = round(statistics.mean(g))
    b_avg = round(statistics.mean(b))

    rgb_avg = tuple((r_avg, g_avg, b_avg))

    hex_code = '#%02x%02x%02x' % rgb_avg

    return hex_code
