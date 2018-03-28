import spotipy
import spotipy.util as util
import os


client_id = os.environ['CLIENT_ID']
secret_key = os.environ['CLIENT_SECRET']


token = util.prompt_for_user_token(
        username='1243461497',
        scope='',
        client_id='f5e9ea13aa4448af8db66232ee23ff0e',
        client_secret='3539d4578116459ab8957fc5ffa03cc5',
        redirect_uri='http://google.com/'
)

spotify = spotipy.Spotify(auth=token)
