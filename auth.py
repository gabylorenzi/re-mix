import spotipy
from spotipy.oauth2 import SpotifyOAuth
import keys 

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=keys.CLIENT_ID, client_secret=keys.CLIENT_SECRET, redirect_uri=keys.REDIRECT_URI, scope=keys.SCOPE))
print(sp)
print("auth headers", sp._auth_headers())
results = sp.current_user_top_tracks(limit=50, offset=0, time_range="short_term")
print(results['items'])

curr_usr_top_tracks = []
for idx, item in enumerate(results['items']):
    track = item['uri'].encode()[14:]
    curr_usr_top_tracks.append(track)
    print(idx, track, item['name']) 

print(curr_usr_top_tracks)
