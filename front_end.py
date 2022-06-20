import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import keys 

scope = "user-library-read"
st.header('Welcome to Re-Mix.')
st.write("""Spotify's Discover Weekly is great. But sometimes we want more. 
            **Re-Mix** is a different approach on the weekly recommendation system we love so much.
            We'll walk you through how we will build a playlist we hope you'll love.
            And if you don't love it, give it a few days and try again.""")

if st.button("Click to begin."):
    st.write('I am Re-Mix, nice to meet you. What is your username?')
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=keys.CLIENT_ID, client_secret=keys.CLIENT_SECRET, redirect_uri=keys.REDIRECT_URI, scope=keys.SCOPE))
