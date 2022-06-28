from email.mime import base
import random
import string

from matplotlib import artist
#from app import BASE_URL, access_token, headers
import requests

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import keys 
from datetime import datetime

def get_song_name_from_uri(sp, uri):
    """Returns string representation of song name"""
    return sp.track(uri)

def get_curr_users_top_tracks(sp, time_range="short_term"):
    """
    Returns list of spotify URIs in string format representing the current user's top tracks"""
    results = sp.current_user_top_tracks(limit=50, offset=0, time_range=time_range)

    curr_usr_top_tracks = []
    for idx, item in enumerate(results['items']):
        track = item['uri'][14:]
        curr_usr_top_tracks.append(track)
    return curr_usr_top_tracks


def get_curr_users_top_artists(sp, time_range='short_term'):
    "Returns 30 of the users top artists in a given time range"
    return sp.current_user_top_artists(limit = 30, time_range = time_range)


def get_last_weeks_artists():
    """
    Returns a list of strings, each being an artist ID that have had more than a threshold of listens for the last week. 
    The threshold [how_many_listens] can indicate how popular an artist is for the user.
    """
    #these variables come from import app.py
    #r = requests.get(BASE_URL + 'me/top/tracks', headers=headers)
    #print(r)

def get_last_weeks_listens(artist_id = string) -> int:
    """
    Returns an integer equivalent to the number of listens by a given artist, taking the artist ID as input
    """
    return None

def get_random_ids(song_ids: list, sample_prop: int) -> list:
    """
    Given an input of various song IDs, return a random subset of song IDs equal to the sample size of the parameter passed in.
    Parameters:
        song_ids: a list of spotify song IDs
        sample_size: a decimal proportion of the number of songs that would be the sample (100 song ids, .1 sample size would return 10 ids)
    """
    return random.sample(song_ids, sample_prop * len(song_ids)) 
    
def get_artists_latest_release(artist_id: string) -> string:
    """
    Given an artist id, return the songs that were released prior to the recency set within the function.
    Parameter: 
        artist_id: spotify artist id for which 
    """
    import datetime 
    recency = datetime.today() #TO DO : get today's date and then take a week before that 
    return ""

def get_related_artist(sp, artist_id: string):
    return sp.artist_related_artists(artist_id)

def get_top_genre():
    return None

def get_similar_song(sp, song_ids: list) -> string:
    """
    Given a random set of top songs, get recommendations.

    Parameters:
        song_id: spotify song id for which audio features will be compared
    """

    audio_features = sp.audio_features(song_ids)
    return None

def get_audio_features(sp, song_ids: list) -> dict:
    """
    Given a song id (can take up to 50), returns the dictionary of audio features for the song. 
    #idk if i need this function
    """

    return sp.audio_features(song_ids)

def get_similar_songs(sp, base_list = list) -> list:
    """
    Given a song URI, artists, or genre, return the recommendations. Can pass in multiple songs.
    Returns a list of URIs.
    https://spotipy.readthedocs.io/en/2.9.0/#spotipy.client.Spotify.recommendations
    """
    if len(base_list) > 5:
        raise ValueError('list must be 5 items or less')
    raw_recs = sp.recommendations(seed_tracks = base_list, limit = 10)
    recommendations = []
    for item in raw_recs['tracks']:
        recommendations.append(item['id'])
    return recommendations


def main():
    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=keys.CLIENT_ID, client_secret=keys.CLIENT_SECRET, redirect_uri=keys.REDIRECT_URI, scope=keys.SCOPE))
