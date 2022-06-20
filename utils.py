from random import sample
import string
from app import BASE_URL, access_token, headers
import requests

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import keys 
from datetime import datetime

def get_song_name_from_uri(sp, uri):
    """Returns string representation of """
    return sp.track(uri)

def get_curr_users_top_tracks(sp, time_range="short_term"):
    """
    Returns list of spotify URIs in string format representing the current user's top tracks"""
    results = sp.current_user_top_tracks(limit=50, offset=0, time_range=time_range)
    print(results['items'])

    curr_usr_top_tracks = []
    for idx, item in enumerate(results['items']):
        track = item['uri'].encode()[14:]
        curr_usr_top_tracks.append(track)

    return curr_usr_top_tracks


def get_last_weeks_artists():
    """
    Returns a list of strings, each being an artist ID that have had more than a threshold of listens for the last week. 
    The threshold [how_many_listens] can indicate how popular an artist is for the user.
    """

    r = requests.get(BASE_URL + 'me/top/tracks', headers=headers)
    print(r)

def get_last_weeks_listens(artist_id = string) -> int:
    """
    Returns an integer equivalent to the number of listens by a given artist, taking the artist ID as input
    """
    return None

def get_last_weeks_artists():
    return None

def get_random_ids(song_ids: list, sample_size: int) -> list:
    """
    Given an input of various song IDs, return a random subset of song IDs equal to the sample size of the parameter passed in.
    Parameters:
        song_ids: a list of spotify song IDs
        sample_size: a decimal proportion of the number of songs that would be the sample (100 song ids, .1 sample size would return 10 ids)
    """

    random_ids = song_ids.random(sample_size) #TO DO: something like this

    return random_ids
    
def get_artists_latest_release(artist_id: string) -> string:
    """
    Given an artist id, return the songs that were released prior to the recency set within the function.
    Parameter: 
        artist_id: spotify artist id for which 
    """
    import datetime 
    recency = datetime.today() #TO DO : get today's date and then take a week before that 
    return ""

def get_top_genre():
    return None

def get_similar_song(song_id: string) -> string:
    """
    Given a song_id, find 3 songs with similar audio features. 

    Parameters:
        song_id: spotify song id for which audio features will be compared
    """

    audio_features = get_audio_features(song_id)
    return None

def get_audio_features(song_id: string) -> dict:
    """
    Given a song id, returns the dictionary of audio features for the song. 
    """
    #TO DO: call the api to get audio features of any given song given the song_id
    return {}

def main():
    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=keys.CLIENT_ID, client_secret=keys.CLIENT_SECRET, redirect_uri=keys.REDIRECT_URI, scope=keys.SCOPE))
