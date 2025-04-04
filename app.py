import streamlit as st
import pandas as pd
from utils.spotify_api import create_spotify_client, get_recent_tracks
from utils.spotify_api import get_audio_features
import plotly.graph_objects as go

st.set_page_config(page_title="MeloMix", layout="wide")
st.title("🎧 MeloMix")
st.subheader("Explora tu huella musical en Spotify")

# Inicializamos el estado si no existe
if "sp" not in st.session_state:
    sp, auth_url = create_spotify_client()
    if sp:
        st.session_state["sp"] = sp
        st.session_state["auth_url"] = None
    else:
        st.session_state["auth_url"] = auth_url

sp = st.session_state.get("sp", None)
auth_url = st.session_state.get("auth_url", None)

# UI según estado de sesión
if auth_url:
    st.warning("Para continuar, inicia sesión con Spotify:")
    st.markdown(f"[🔐 Iniciar sesión en Spotify]({auth_url})")
elif sp:
    st.success("✅ Autenticado correctamente")
    st.write("🎵 Aquí va tu resumen musical reciente...")

    tracks = get_recent_tracks(sp)
    df = pd.DataFrame(tracks)

    # Mostrar tabla
    st.dataframe(df.head())

    # Obtener audio features
    track_ids = df["track_id"].dropna().tolist()
    features = get_audio_features(sp, track_ids)

    # Convertir a DataFrame
    features_df = pd.DataFrame(features)

    # Seleccionar features interesantes y promediarlas
    cols = ["danceability", "energy", "valence", "acousticness", "instrumentalness", "speechiness"]
    promedios = features_df[cols].mean().round(2)

    # Crear Radar Chart
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=promedios.values,
        theta=promedios.index,
        fill="toself",
        name="Promedio de audio features"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1])
        ),
        showlegend=False,
        title="🎚️ Perfil sonoro promedio (últimas 50 canciones)"
    )

    st.plotly_chart(fig)

    # Métricas rápidas
    st.metric("🎵 Canciones", len(df))
    st.metric("🎤 Artistas únicos", df["artist"].nunique())

    # Gráfico de canciones por hora
    df["played_at"] = pd.to_datetime(df["played_at"])
    df["hora"] = df["played_at"].dt.hour
    hist = df["hora"].value_counts().sort_index()

    st.bar_chart(hist)
else:
    st.error("❌ Ocurrió un error durante la autenticación.")
