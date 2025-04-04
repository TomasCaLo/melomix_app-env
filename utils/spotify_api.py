import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import streamlit as st

# Cargar variables del entorno (.env)
load_dotenv()

def create_spotify_client():
    sp_oauth = SpotifyOAuth(
        scope="user-read-recently-played user-top-read",
        show_dialog=True
    )

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        # Obtener el código de autorización desde la URL (después del login)
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"][0]
            try:
                token_info = sp_oauth.get_access_token(code)
                sp = spotipy.Spotify(auth=token_info["access_token"])
                return sp, None
            except:
                return None, sp_oauth.get_authorize_url()
        else:
            # Aún no hay código, redirigimos al login
            auth_url = sp_oauth.get_authorize_url()
            return None, auth_url
    else:
        # Token válido, creamos cliente de Spotify
        sp = spotipy.Spotify(auth=token_info["access_token"])
        return sp, None


def get_recent_tracks(sp, limit=50):
    results = sp.current_user_recently_played(limit=limit)
    
    tracks_data = []
    for item in results["items"]:
        track = item["track"]
        played_at = item["played_at"]

        track_info = {
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "release_date": track["album"]["release_date"],
            "played_at": played_at,
            "track_id": track["id"]  # Lo dejamos por si lo necesitas luego
        }
        tracks_data.append(track_info)

    return tracks_data
