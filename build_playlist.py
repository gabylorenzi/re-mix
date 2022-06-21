import spotipy

def build_playlist_add_tracks(sp, user, tracks:list, playlist_name:str, description: str):
    id = sp.user_playlist_create(user, playlist_name, description)
    sp.user_playlist_add_tracks(user, id, tracks)
