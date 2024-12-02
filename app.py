import pandas as pd
import streamlit as st
import re
from PIL import Image
import requests
from io import BytesIO

# Configuration de la page Streamlit
st.set_page_config(page_title="Collection de Jeux", layout="wide")

# Fonction pour charger les données depuis l'URL du Google Sheets
def load_data(sheet_url):
    """Load data from a public Google Sheets URL."""
    try:
        df = pd.read_csv(sheet_url)
        df.columns = [col.strip().lower() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()

# Fonction pour formater `nombre_de_joueur`
def format_players(players):
    """Convert player numbers from '2 - 5' format to tuple or integer."""
    try:
        numbers = re.findall(r'\d+', str(players))
        if not numbers:
            return None
        if len(numbers) == 1:
            return int(numbers[0])
        return (int(numbers[0]), int(numbers[1]))
    except:
        return None

# Fonction pour formater `temps_de_jeu`
def format_duration(duration):
    """Convert game duration from '30 - 60' to tuple or integer."""
    try:
        numbers = re.findall(r'\d+', str(duration))
        if not numbers:
            return None
        if len(numbers) == 1:
            return int(numbers[0])
        return (int(numbers[0]), int(numbers[1]))
    except:
        return None

# Fonction pour télécharger et redimensionner les images
def fetch_image(url, size=(50, 50)):
    """Fetch and return a resized image from a URL."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            return image.resize(size)
        else:
            return None
    except:
        return None

# Fonction principale
def main():
    st.title("🎲 Ma Collection de Jeux de Société")
    
    # Charger les données
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQk9d7G5-vwgujvUjgVvHg40wNrYqdtRt8ujK0C1fZkeFE4SjTXd_R-4khNytAPgb6wRKRSlT7kYEZV/pub?gid=0&single=true&output=csv"
    df = load_data(SHEET_URL)

    if df.empty:
        st.error("Impossible de charger les données. Vérifiez le lien public.")
        return

    # Nettoyer les colonnes
    df['nombre_de_joueur'] = df['nombre_de_joueur'].apply(format_players)
    df['temps_de_jeu'] = df['temps_de_jeu'].apply(format_duration)

    # Filtres dans la barre latérale
    st.sidebar.header("Filtres")

    # Filtre par mécanisme
    if 'mécanisme' in df.columns:
        mecanismes = df['mécanisme'].dropna().unique().tolist()
        selected_mecanismes = st.sidebar.multiselect("Mécanismes", mecanismes)
        if selected_mecanismes:
            df = df[df['mécanisme'].isin(selected_mecanismes)]

    # Filtre par nombre de joueurs
    num_players = st.sidebar.slider("Nombre de joueurs (min-max)", 1, 20, (1, 5))
    df = df[df['nombre_de_joueur'].apply(
        lambda x: (
            isinstance(x, tuple) and x[0] <= num_players[1] and x[1] >= num_players[0]
        ) or (
            isinstance(x, int) and num_players[0] <= x <= num_players[1]
        )
    )]

    # Filtre par temps de jeu
    game_duration = st.sidebar.slider("Temps de jeu (minutes, min-max)", 0, 180, (0, 60))
    df = df[df['temps_de_jeu'].apply(
        lambda x: (
            isinstance(x, tuple) and x[0] <= game_duration[1] and x[1] >= game_duration[0]
        ) or (
            isinstance(x, int) and game_duration[0] <= x <= game_duration[1]
        )
    )]

    # Afficher les jeux
    st.subheader(f"🃏 Jeux ({len(df)} trouvés)")

    for _, jeu in df.iterrows():
        # Télécharger la miniature
        thumbnail = fetch_image(jeu['image'], size=(50, 50)) if pd.notna(jeu['image']) else None

        # Construire le titre de l'expander
        if pd.notna(jeu['récap']):
            title = f"{jeu['noms']} ({jeu['récap']})"
        else:
            title = jeu['noms']

        # Ajouter l'image et le titre ensemble
        if thumbnail:
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                st.image(thumbnail, use_column_width=True)
            with col2:
                with st.expander(title):
                    # Contenu de l'expander
                    st.metric("Note", f"{jeu['note']}/5" if pd.notna(jeu['note']) else "Non noté")
                    st.metric("Durée", f"{jeu['temps_de_jeu'][0]}-{jeu['temps_de_jeu'][1]} minutes" if isinstance(jeu['temps_de_jeu'], tuple) else f"{jeu['temps_de_jeu']} minutes")
                    st.metric("Joueurs", f"{jeu['nombre_de_joueur'][0]}-{jeu['nombre_de_joueur'][1]} joueurs" if isinstance(jeu['nombre_de_joueur'], tuple) else f"{jeu['nombre_de_joueur']} joueurs")

                    if pd.notna(jeu['règles']):
                        st.markdown(f"[📖 Règles]({jeu['règles']})")

                    st.write(f"**Mécanismes**: {jeu['mécanisme']}")
                    st.write(f"**Description**: {jeu['récap']}")

        else:
            with st.expander(title):
                st.metric("Note", f"{jeu['note']}/5" if pd.notna(jeu['note']) else "Non noté")
                st.metric("Durée", f"{jeu['temps_de_jeu'][0]}-{jeu['temps_de_jeu'][1]} minutes" if isinstance(jeu['temps_de_jeu'], tuple) else f"{jeu['temps_de_jeu']} minutes")
                st.metric("Joueurs", f"{jeu['nombre_de_joueur'][0]}-{jeu['nombre_de_joueur'][1]} joueurs" if isinstance(jeu['nombre_de_joueur'], tuple) else f"{jeu['nombre_de_joueur']} joueurs")

                if pd.notna(jeu['règles']):
                    st.markdown(f"[📖 Règles]({jeu['règles']})")

                st.write(f"**Mécanismes**: {jeu['mécanisme']}")
                st.write(f"**Description**: {jeu['récap']}")

# Exécuter l'application
if __name__ == "__main__":
    main()
