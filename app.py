import pandas as pd
import streamlit as st
import re
from typing import Tuple, List

def validate_and_clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Validate and clean DataFrame columns."""
    if df.empty:
        st.error("Le DataFrame est vide. Vérifiez votre source de données.")
        return df, ["Aucune donnée chargée"]

    df_clean = df.copy()
    
    # Normalize column names
    df_clean.columns = [col.strip().lower() for col in df_clean.columns]
    
    # Required columns
    required_columns = ['noms', 'temps_de_jeu', 'nombre_de_joueur', 'mécanisme', 'récap', 'note', 'image', 'règles']
    
    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in df_clean.columns]
    if missing_columns:
        st.error(f"Colonnes manquantes : {', '.join(missing_columns)}")
        return df_clean, [f"Colonnes manquantes : {', '.join(missing_columns)}"]

    # Type conversion and cleaning
    df_clean['noms'] = df_clean['noms'].astype(str).str.strip()
    df_clean['temps_de_jeu'] = df_clean['temps_de_jeu'].astype(str).str.strip()
    df_clean['nombre_de_joueur'] = df_clean['nombre_de_joueur'].astype(str).str.strip()
    df_clean['mécanisme'] = df_clean['mécanisme'].astype(str).str.strip()
    df_clean['récap'] = df_clean['récap'].astype(str).str.strip()
    
    # Note validation
    try:
        df_clean['note'] = pd.to_numeric(df_clean['note'], errors='coerce')
        invalid_notes = df_clean[(df_clean['note'].notna()) & ((df_clean['note'] < 0) | (df_clean['note'] > 5))]
        if not invalid_notes.empty:
            st.warning(f"Notes invalides détectées: {len(invalid_notes)} entrées hors de la plage 0-5")
    except Exception as e:
        st.error(f"Erreur lors de la validation des notes : {e}")

    return df_clean, []

def format_game_duration(duration_str: str) -> str:
    """Format game duration consistently."""
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
    except Exception:
        return duration_str

def format_player_count(players_str: str) -> str:
    """Format player count consistently."""
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
    except Exception:
        return players_str

def add_custom_styles():
    """Add custom CSS styles to the application."""
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
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    """Load data from Google Sheets URL."""
    try:
        df = pd.read_csv(url, encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"Erreur de chargement des données : {e}")
        return pd.DataFrame()

def main():
    # Page configuration
    st.set_page_config(page_title="Collection de Jeux de Société", layout="wide")
    add_custom_styles()
    
    st.title("🎲 Ma Collection de Jeux de Société")
    
    # Google Sheet configuration
    SHEET_ID = "1itKcj2L9HyA0GBIFcRTeQ8-OiIOI5eqw23-vvgXI5pQ"
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
    
    # Load data
    df = load_data(SHEET_URL)
    
    if df.empty:
        st.error("Impossible de charger les données. Vérifiez votre connexion internet ou l'URL.")
        return
    
    # Validate and clean data
    df_clean, validation_results = validate_and_clean_data(df)
    
    # Display validation warnings
    for result in validation_results:
        st.warning(result)
    
    # Sidebar for filtering
    st.sidebar.header("Filtres de Recherche")
    
    # Mechanism filter
    unique_mechanisms = df_clean['mécanisme'].dropna().unique().tolist()
    selected_mechanisms = st.sidebar.multiselect(
        "Sélectionnez les mécanismes", 
        options=unique_mechanisms
    )
    
    # Filter dataframe
    filtered_df = df_clean.copy()
    if selected_mechanisms:
        filtered_df = filtered_df[filtered_df['mécanisme'].isin(selected_mechanisms)]
    
    # Display game count
    st.subheader(f"🃏 Jeux ({len(filtered_df)} trouvés)")
    
    # Display games
    for _, row in filtered_df.iterrows():
        with st.expander(row['noms']):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Game image
                st.image(row['image'] if pd.notna(row['image']) else 'https://via.placeholder.com/200', width=200)
            
            with col2:
                # Game details
                st.metric("Note", f"{row['note']}/5" if pd.notna(row['note']) else "Non noté")
                st.metric("Durée", format_game_duration(row['temps_de_jeu']))
                st.metric("Joueurs", format_player_count(row['nombre_de_joueur']))
                
                # Rules button
                if pd.notna(row['règles']):
                    st.link_button("📖 Règles", row['règles'])
                
                # Mechanisms and description
                st.write(f"**Mécanismes**: {row['mécanisme']}")
                st.write(f"**Description**: {row['récap']}")

if __name__ == "__main__":
    main()
