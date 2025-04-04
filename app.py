import streamlit as st
import pandas as pd
from utils.spotify_api import create_spotify_client, get_recent_tracks

st.set_page_config(page_title="MeloMix", layout="wide")
st.title("🎧 MeloMix")
st.subheader("Explora tu huella musical en Spotify")

# Inicializamos el estado de sesión para mantener el cliente activo
if "sp" not in st.session_state:
    sp, auth_url = create_spotify_client()
    if sp:
        st.session_state["sp"] = sp
        st.session_state["auth_url"] = None
    else:
        st.session_state["auth_url"] = auth_url

sp = st.session_state.get("sp", None)
auth_url = st.session_state.get("auth_url", None)

# Interfaz: login o datos
if auth_url:
    st.warning("Para continuar, inicia sesión con Spotify:")
    st.markdown(f"[🔐 Iniciar sesión en Spotify]({auth_url})")
elif sp:
    st.success("✅ Autenticado correctamente")
    st.write("🎵 Tus 50 canciones reproducidas más recientes:")

    tracks = get_recent_tracks(sp)
    df = pd.DataFrame(tracks)

    # Tabla de canciones
    st.dataframe(df[["played_at", "track_name", "artist", "album", "release_date"]].head(50))

    # Métricas clave
    st.markdown("### 📊 Métricas rápidas")
    st.metric("🎵 Canciones", len(df))
    st.metric("🎤 Artistas únicos", df["artist"].nunique())

    # Histograma de horas de reproducción
    df["played_at"] = pd.to_datetime(df["played_at"]).dt.tz_convert("America/Bogota")
    df["hora"] = df["played_at"].dt.hour
    hist = df["hora"].value_counts().sort_index()

    st.markdown("### ⏰ Horas en que escuchaste música")
    st.bar_chart(hist)
else:
    st.error("❌ Ocurrió un error durante la autenticación.")
