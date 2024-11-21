import pandas as pd
import streamlit as st
import re

# Configuration Google Sheets
SHEET_ID = "1itKcj2L9HyA0GBIFcRTeQ8-OiIOI5eqw23-vvgXI5pQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def load_data(url):
    """Charger les données depuis l'URL Google Sheets"""
    try:
        # Lire le CSV en spécifiant l'encodage
        df = pd.read_csv(url, encoding='utf-8')
        
        # Nettoyer les noms de colonnes
        df.columns = [col.strip().lower() for col in df.columns]
        
        return df
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        return pd.DataFrame()

def format_duration(duration):
    """Formater la durée du jeu"""
    try:
        numbers = re.findall(r'\d+', str(duration))
        if not numbers:
            return "Durée non spécifiée"
        return f"{numbers[0]} minutes" if len(numbers) == 1 else f"{numbers[0]}-{numbers[1]} minutes"
    except:
        return str(duration)

def format_players(players):
    """Formater le nombre de joueurs"""
    try:
        numbers = re.findall(r'\d+', str(players))
        if not numbers:
            return "Nombre de joueurs non spécifié"
        return f"{numbers[0]} joueurs" if len(numbers) == 1 else f"{numbers[0]}-{numbers[1]} joueurs"
    except:
        return str(players)

def main():
    st.set_page_config(page_title="Collection de Jeux", layout="wide")
    st.title("🎲 Ma Collection de Jeux de Société")

    # Charger les données
    df = load_data(SHEET_URL)

    if df.empty:
        st.error("Impossible de charger les données. Vérifiez votre connexion.")
        return

    # Vérifier les colonnes requises
    required_columns = ['noms', 'temps_de_jeu', 'nombre_de_joueur', 'mécanisme', 'récap', 'note', 'image', 'règles']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Colonnes manquantes : {', '.join(missing_columns)}")
        st.write("Colonnes présentes :", list(df.columns))
        return

    # Filtres dans la sidebar
    st.sidebar.header("Filtres")
    
    # Mécanismes uniques
    if 'mécanisme' in df.columns:
        mecanismes = df['mécanisme'].dropna().unique().tolist()
        selected_mecanismes = st.sidebar.multiselect("Mécanismes", mecanismes)
        
        # Filtrage
        if selected_mecanismes:
            df = df[df['mécanisme'].isin(selected_mecanismes)]

    # Afficher les jeux
    st.subheader(f"🃏 Jeux ({len(df)} trouvés)")

    for _, jeu in df.iterrows():
        with st.expander(jeu['noms']):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Image du jeu
                st.image(jeu['image'] if pd.notna(jeu['image']) else 'https://via.placeholder.com/200', width=200)
            
            with col2:
                # Détails du jeu
                st.metric("Note", f"{jeu['note']}/5" if pd.notna(jeu['note']) else "Non noté")
                st.metric("Durée", format_duration(jeu['temps_de_jeu']))
                st.metric("Joueurs", format_players(jeu['nombre_de_joueur']))
                
                # Bouton règles
                if pd.notna(jeu['règles']):
                    st.link_button("📖 Règles", jeu['règles'])
                
                # Mécanismes et description
                st.write(f"**Mécanismes**: {jeu['mécanisme']}")
                st.write(f"**Description**: {jeu['récap']}")

if __name__ == "__main__":
    main()
