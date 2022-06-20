import spotipy

def build_playlist_add_tracks(sp, user, playlist_id, tracks:list, playlist_name:str, description: str):
    sp.user_playlist_create(user, playlist_name, description)
    sp.user_playlist_add_tracks(user, playlist_id, tracks)
