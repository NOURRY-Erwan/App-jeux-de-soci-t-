import pandas as pd
import streamlit as st
import re
from typing import Tuple, List

# Configuration de base
SHEET_ID = "1itKcj2L9HyA0GBIFcRTeQ8-OiIOI5eqw23-vvgXI5pQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def validate_and_clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Valide et nettoie les données du DataFrame."""
    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.strip()
    
    column_types = {
        'Noms': str,
        'temps_de_jeu': str,
        'Nombre_de_joueur': str,
        'mécanisme': str,
        'récap': str,
        'Boite de jeu': str,
        'Règles': str,
        'image': str,
        'Avis': str,
        'Note': float
    }
    
    for col, dtype in column_types.items():
        if col in df_clean.columns:
            try:
                if dtype == str:
                    df_clean[col] = df_clean[col].astype(str).replace('nan', '').str.strip()
                elif dtype == float:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            except Exception as e:
                st.warning(f"Erreur lors de la conversion de la colonne {col}: {str(e)}")
    
    validation_results = []
    
    if 'Note' in df_clean.columns:
        invalid_notes = df_clean[
            (df_clean['Note'].notna()) & 
            ((df_clean['Note'] < 0) | (df_clean['Note'] > 5))
        ]
        if not invalid_notes.empty:
            validation_results.append(
                f"Notes invalides détectées: {len(invalid_notes)} entrées hors de la plage 0-5"
            )
    
    return df_clean, validation_results

def format_game_duration(duration_str: str) -> str:
    """Formate la durée du jeu de manière cohérente."""
    try:
        numbers = [int(n) for n in re.findall(r'\d+', str(duration_str))]
        if not numbers:
            return "Durée non spécifiée"
        if len(numbers) == 1:
            return f"{numbers[0]} minutes"
        elif len(numbers) == 2:
            return f"{numbers[0]}-{numbers[1]} minutes"
        else:
            return duration_str
    except ValueError:
        return duration_str

def format_player_count(players_str: str) -> str:
    """Formate le nombre de joueurs de manière cohérente."""
    try:
        numbers = [int(n) for n in re.findall(r'\d+', str(players_str))]
        if not numbers:
            return "Nombre non spécifié"
        if len(numbers) == 1:
            return f"{numbers[0]} joueurs"
        elif len(numbers) == 2:
            return f"{numbers[0]}-{numbers[1]} joueurs"
        else:
            return players_str
    except ValueError:
        return players_str

def add_custom_styles():
    """Ajoute des styles CSS personnalisés à l'application."""
    st.markdown("""
    <style>
    .stExpander {
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    """Charge les données depuis l'URL Google Sheets."""
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Erreur de chargement des données : {e}")
        return pd.DataFrame()

def main():
    # Configuration de la page
    st.set_page_config(
        page_title="Collection de Jeux de Société", 
        layout="wide", 
        initial_sidebar_state="expanded"
    )
    add_custom_styles()
    
    # Titre principal
    st.title("🎲 Ma Collection de Jeux de Société")
    
    # Chargement des données
    df = load_data(SHEET_URL)
    
    # Validation des données
    df_clean, validation_results = validate_and_clean_data(df)
    
    # Affichage des résultats de validation
    if validation_results:
        for result in validation_results:
            st.warning(result)
    
    # Sidebar pour filtres
    st.sidebar.header("Filtres de Recherche")
    
    # Filtres dynamiques
    selected_mechanism = st.sidebar.multiselect(
        "Sélectionnez les mécanismes", 
        options=df_clean['mécanisme'].dropna().unique()
    )
    
    selected_duration = st.sidebar.slider(
        "Durée de jeu (minutes)", 
        min_value=0, 
        max_value=int(df_clean['temps_de_jeu'].str.extract('(\d+)').astype(float).max()[0]),
        value=(0, 120)
    )
    
    # Filtrage des données
    filtered_df = df_clean.copy()
    
    if selected_mechanism:
        filtered_df = filtered_df[filtered_df['mécanisme'].isin(selected_mechanism)]
    
    # Affichage des jeux
    st.subheader(f"🃏 Jeux ({len(filtered_df)} trouvés)")
    
    for index, row in filtered_df.iterrows():
        with st.expander(row['Noms']):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Image du jeu
                st.image(row['image'] if pd.notna(row['image']) else 'https://via.placeholder.com/200', width=200)
            
            with col2:
                # Détails du jeu
                st.metric("Note", f"{row['Note']}/5" if pd.notna(row['Note']) else "Non noté")
                st.metric("Durée", format_game_duration(row['temps_de_jeu']))
                st.metric("Joueurs", format_player_count(row['Nombre_de_joueur']))
                
                # Boutons d'action
                if pd.notna(row['Règles']):
                    st.link_button("📖 Règles", row['Règles'])
                
                # Mécanismes
                st.write(f"**Mécanismes**: {row['mécanisme']}")
                
                # Récapitulatif
                st.write(f"**Description**: {row['récap']}")

if __name__ == "__main__":
    main()
