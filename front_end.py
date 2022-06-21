import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import keys 
import utils
import build_playlist

scope = "user-library-read"
st.header('Welcome to Re-Mix.')
st.write("""Spotify's Discover Weekly is great. But sometimes we want more. 
            **Re-Mix** is a different approach on the weekly recommendation system we love so much.
            We'll walk you through how we will build a playlist we hope you'll love.
            And if you don't love it, give it a few days and try again.""")

if st.button("Click to begin."):
    st.write('I am Re-Mix, nice to meet you.')
    st.write('')

    def build():
        st.write('')
        st.write('Let\'s build a playlist.')

    def title():
        playlist_title = st.text_input('What do you want to name today\'s playlist?', on_change=build)

    st.text_input('What is your username?', on_change=title)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=keys.CLIENT_ID, client_secret=keys.CLIENT_SECRET, redirect_uri=keys.REDIRECT_URI, scope=keys.SCOPE))
    
    if sp is not None:
        st.success('Now connected to Spotify.')
        st.write('')
        playlist_title = st.text_input('What do you want to name today\'s playlist?', on_change=build)

    top_tracks = utils.get_curr_users_top_tracks(sp)
    print(type(top_tracks))
    print(top_tracks)
    st.write('Building playlist with your top tracks')
    playlist = sp.user_playlist_create('lorenziga', name="test top tracks", description="if ur reading this im a better coder than i thought")
    st.write(playlist['id'])
    sp.user_playlist_add_tracks('lorenziga', "774rZ87YGPEE8Kh6C13jqL", tracks = ['4lKSHi12cKgQlXwkrPHQ6s'])
