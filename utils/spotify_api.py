import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import streamlit as st
from urllib.parse import urlparse, parse_qs

def create_spotify_client():
    load_dotenv()

    sp_oauth = SpotifyOAuth(
        scope="user-read-recently-played user-top-read",
        show_dialog=True
    )

    # Intentamos primero obtener token en caché
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        # Si no hay token en caché, tratamos de extraer el código de la URL actual
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"][0]
            token_info = sp_oauth.get_access_token(code)
            sp = spotipy.Spotify(auth=token_info["access_token"])
            return sp, None
        else:
            # No hay token ni código, toca pedir autorización
            auth_url = sp_oauth.get_authorize_url()
            return None, auth_url
    else:
        # Ya hay token guardado
        sp = spotipy.Spotify(auth=token_info["access_token"])
        return sp, None
        return sp, None


def get_recent_tracks(sp, limit=50):
    results = sp.current_user_recently_played(limit=limit)
    
    tracks_data = []
    for item in results["items"]:
        track = item["track"]
        played_at = item["played_at"]

        track_info = {
            "track_id": track["id"],  # 👈 Añadimos el ID
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "release_date": track["album"]["release_date"],
            "played_at": played_at
        }
        tracks_data.append(track_info)

    return tracks_data

def get_audio_features(sp, track_ids):
    features = []

    # Eliminar IDs duplicados
    unique_ids = list(set(track_ids))

    # Procesar en chunks de 100 (por si acaso)
    for i in range(0, len(unique_ids), 100):
        batch = unique_ids[i:i+100]
        batch_features = sp.audio_features(batch)
        features.extend(batch_features)

    return features

