import pandas as pd
import streamlit as st
from typing import Optional, Tuple, List, Dict
import re

# Constante pour le lien Google Sheets
SHEET_ID = "1itKcj2L9HyA0GBIFcRTeQ8-OiIOI5eqw23-vvgXI5pQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def validate_and_clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Valide et nettoie les données du DataFrame."""
    
    # Copie du DataFrame pour éviter les modifications sur l'original
    df_clean = df.copy()
    
    # Nettoyage des noms de colonnes
    df_clean.columns = df_clean.columns.str.strip()
    
    # Mapping des types de données attendus
    column_types = {
        'Noms': str,
        'note': float,
        'Nombre_de_joueur': str,
        'temps_de_jeu': str,
        'mécanisme': str,
        'avis': str,
        'Règles': str,  # Colonne G
        'Boite_de_jeu': str  # Colonne F
    }
    
    # Conversion et nettoyage des colonnes
    for col, dtype in column_types.items():
        if col in df_clean.columns:
            try:
                if dtype == str:
                    df_clean[col] = df_clean[col].astype(str).replace('nan', '').str.strip()
                elif dtype == float:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            except Exception as e:
                st.warning(f"Erreur lors de la conversion de la colonne {col}: {str(e)}")
    
    # Validation des données
    validation_results = []
    
    # Vérification des valeurs de notes
    if 'note' in df_clean.columns:
        invalid_notes = df_clean[
            (df_clean['note'].notna()) & 
            ((df_clean['note'] < 0) | (df_clean['note'] > 5))
        ]
        if not invalid_notes.empty:
            validation_results.append(
                f"Notes invalides détectées: {len(invalid_notes)} entrées hors de la plage 0-5"
            )
    
    # Vérification des URLs pour Règles (PDF links)
    url_columns = ['Règles']
    for col in url_columns:
        if col in df_clean.columns:
            invalid_urls = df_clean[
                (df_clean[col].notna()) & 
                (~df_clean[col].str.contains(r'https?://.*\.pdf$', regex=True, na=False))
            ]
            if not invalid_urls.empty:
                validation_results.append(
                    f"URLs invalides dans {col}: {len(invalid_urls)} entrées qui ne sont pas des liens PDF"
                )
    
    return df_clean, validation_results

def display_games_grid(jeux_filtres: pd.DataFrame, cols_per_row: int = 3):
    """Affiche les jeux en mode galerie avec des cartes plus visuelles"""
    cols = st.columns(cols_per_row)
    
    for idx, jeu in enumerate(jeux_filtres.itertuples()):
        with cols[idx % cols_per_row]:
            with st.container(border=True):  # Conteneur avec bordure
                # Image du jeu avec une hauteur fixe
                if hasattr(jeu, 'Boite_de_jeu') and pd.notna(jeu.Boite_de_jeu) and str(jeu.Boite_de_jeu).startswith('http'):
                    st.image(jeu.Boite_de_jeu, use_column_width=True, height=250)
                else:
                    st.image("https://via.placeholder.com/250x250?text=Pas+d'image", use_column_width=True)
                
                # Titre et note dans un bloc compact
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"#### {jeu.Noms}")
                with col2:
                    if hasattr(jeu, 'note') and pd.notna(jeu.note):
                        st.metric(label="Note", value=f"{jeu.note}/5")
                
                # Informations principales en colonnes
                col1, col2 = st.columns(2)
                with col1:
                    if hasattr(jeu, 'Nombre_de_joueur') and pd.notna(jeu.Nombre_de_joueur):
                        st.markdown(f"🎲 **Joueurs**\n{format_player_count(jeu.Nombre_de_joueur)}")
                
                with col2:
                    if hasattr(jeu, 'temps_de_jeu') and pd.notna(jeu.temps_de_jeu):
                        st.markdown(f"⏱️ **Durée**\n{format_game_duration(jeu.temps_de_jeu)}")
                
               # Mécanisme sur toute la largeur
                if hasattr(jeu, 'mécanisme') and pd.notna(jeu.mécanisme):
                    st.markdown(f"⚙️ **Mécanisme**: {jeu.mécanisme}")
                
                # Bouton pour afficher l'avis et les règles
                col1, col2 = st.columns(2)
                with col1:
                    if hasattr(jeu, 'avis') and pd.notna(jeu.avis):
                        if st.button(f"Voir l'avis", key=f"avis_{idx}"):
                            st.write(jeu.avis)
                
                with col2:
                    if hasattr(jeu, 'Règles') and pd.notna(jeu.Règles) and str(jeu.Règles).startswith('http') and str(jeu.Règles).lower().endswith('.pdf'):
                        st.markdown(f"[📄 Règles]({jeu.Règles})")

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
    except:
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
    except:
        return players_str

def add_custom_styles():
    """Ajoute des styles CSS personnalisés à l'application."""
    st.markdown("""
        <style>
        /* Style pour les cartes de jeux */
        .stExpander {
            background-color: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #dee2e6;
            margin-bottom: 1rem;
        }
        
        /* Style pour les métriques */
        .stMetric {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Style pour les images */
        .stImage {
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Style pour les titres des jeux */
        h3 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Style pour les boutons */
        .stButton > button {
            width: 100%;
            border-radius: 20px;
            margin-top: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

def setup_page():
    """Configure la page Streamlit avec les paramètres initiaux."""
    st.set_page_config(
        page_title="Collection de Jeux de Société",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    add_custom_styles()
    st.title("🎲 Ma Collection de Jeux de Société")

def load_data() -> pd.DataFrame:
    """Charge les données depuis Google Sheets et vérifie l'intégrité des données."""
    try:
        df = pd.read_csv(SHEET_URL)
        
        # Liste des colonnes requises
        required_columns = ['Noms', 'Nombre_de_joueur', 'temps_de_jeu']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Colonnes manquantes dans le fichier: {', '.join(missing_columns)}")
            st.stop()
        
        return df
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        st.write("URL utilisée:", SHEET_URL)
        st.stop()

def create_filters(df: pd.DataFrame):
    """Crée et retourne les filtres pour la collection."""
    with st.sidebar:
        st.subheader("🎯 Filtres")
        
        # Filtre par note minimum
        st.subheader("⭐ Note minimum")
        if 'note' in df.columns:
            note_min = st.slider(
                "Note minimum",
                min_value=float(df['note'].min() or 0),
                max_value=float(df['note'].max() or 5),
                value=0.0,
                step=0.5
            )
        else:
            note_min = 0
        
        # Filtre par nombre de joueurs
        st.subheader("👥 Nombre de joueurs")
        col1, col2 = st.columns(2)
        with col1:
            min_joueurs = st.number_input("Min", min_value=1, max_value=10, value=1)
        with col2:
            max_joueurs = st.number_input("Max", min_value=1, max_value=10, value=4)
        
        # Filtre par temps de jeu
        st.subheader("⏱️ Temps de jeu")
        temps_range = st.slider(
            "Durée (minutes)",
            min_value=0,
            max_value=180,
            value=(0, 120),
            step=15
        )
        
        # Filtre par mécanisme
        if 'mécanisme' in df.columns:
            st.subheader("⚙️ Mécanismes")
            mecanismes_list = sorted([
                m for m in df['mécanisme'].unique() 
                if pd.notna(m) and str(m).strip()
            ])
            mecanismes = st.multiselect(
                "Sélectionner les mécanismes",
                options=mecanismes_list
            )
        else:
            mecanismes = []
            
        # Tri des jeux
        st.subheader("🔄 Tri")
        tri_options = {
            "Nom (A-Z)": "nom_asc",
            "Nom (Z-A)": "nom_desc",
            "Note (↑)": "note_asc",
            "Note (↓)": "note_desc"
        }
        tri_choisi = st.radio("Trier par:", options=list(tri_options.keys()))
            
        # Filtre par texte
        st.subheader("🔍 Recherche")
        search_text = st.text_input("Rechercher un jeu")
        
        return min_joueurs, max_joueurs, temps_range, mecanismes, search_text, note_min, tri_options[tri_choisi]

def filter_games(df: pd.DataFrame, filters) -> pd.DataFrame:
    """Applique les filtres sur le DataFrame avec gestion des erreurs."""
    min_joueurs, max_joueurs, temps_range, mecanismes, search_text, note_min, tri = filters
    
    try:
        # Copie du DataFrame pour éviter les modifications sur l'original
        df_filtered = df.copy()
        
        # Application des filtres avec gestion des erreurs
        mask = pd.Series(True, index=df.index)
        
        # Filtre note minimum
        if 'note' in df.columns:
            mask &= df['note'].fillna(0) >= note_min
        
        # Filtre nombre de joueurs
        try:
            df_filtered['nombres_joueurs'] = df['Nombre_de_joueur'].apply(
                lambda x: [int(n) for n in re.findall(r'\d+', str(x))] or [0]
            )
            joueurs_mask = df_filtered['nombres_joueurs'].apply(
                lambda x: any(min_joueurs <= n <= max_joueurs for n in x if n > 0)
            )
            mask &= joueurs_mask
        except Exception as e:
            st.warning(f"Erreur lors du filtrage par nombre de joueurs: {str(e)}")
        
        # Filtre temps de jeu
        try:
            df_filtered['temps_minutes'] = df['temps_de_jeu'].apply(
                lambda x: next(iter([int(n) for n in re.findall(r'\d+', str(x))]), 0)
            )
            mask &= df_filtered['temps_minutes'].between(temps_range[0], temps_range[1])
        except Exception as e:
            st.warning(f"Erreur lors du filtrage par temps de jeu: {str(e)}")
        
        # Filtre mécanismes
        if mecanismes:
            mecanisme_mask = df['mécanisme'].fillna('').str.lower().apply(
                lambda x: any(m.lower() in x for m in mecanismes)
            )
            mask &= mecanisme_mask
        
        # Filtre texte
        if search_text:
            search_mask = df['Noms'].fillna('').str.contains(
                search_text, case=False, na=False
            )
            if 'avis' in df.columns:
                search_mask |= df['avis'].fillna('').str.contains(
                    search_text, case=False, na=False
                )
            mask &= search_mask
        
        filtered_df = df[mask].copy()
        
        # Application du tri
        try:
            if tri == "nom_asc":
                filtered_df = filtered_df.sort_values('Noms', na_position='last')
            elif tri == "nom_desc":
                filtered_df = filtered_df.sort_values('Noms', ascending=False, na_position='last')
            elif tri == "note_asc" and 'note' in filtered_df.columns:
                filtered_df = filtered_df.sort_values('note', na_position='last')
            elif tri == "note_desc" and 'note' in filtered_df.columns:
                filtered_df = filtered_df.sort_values('note', ascending=False, na_position='last')
        except Exception as e:
            st.warning(f"Erreur lors du tri: {str(e)}")
        
        return filtered_df
    
    except Exception as e:
        st.error(f"Erreur lors du filtrage des jeux: {str(e)}")
        return df

def display_games_grid(jeux_filtres: pd.DataFrame, cols_per_row: int = 3):
    """Affiche les jeux en mode galerie avec des cartes plus visuelles"""
    cols = st.columns(cols_per_row)
    
    for idx, jeu in enumerate(jeux_filtres.itertuples()):
        with cols[idx % cols_per_row]:
            with st.container(border=True):  # Conteneur avec bordure
                # Image du jeu avec une hauteur fixe
                if hasattr(jeu, 'Boite_de_jeu') and pd.notna(jeu.Boite_de_jeu) and str(jeu.Boite_de_jeu).startswith('http'):
                    st.image(jeu.Boite_de_jeu, use_column_width=True, height=250)
                else:
                    st.image("https://via.placeholder.com/250x250?text=Pas+d'image", use_column_width=True)
                
                # Titre et note dans un bloc compact
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"#### {jeu.Noms}")
                with col2:
                    if hasattr(jeu, 'note') and pd.notna(jeu.note):
                        st.metric(label="Note", value=f"{jeu.note}/5")
                
                # Informations principales en colonnes
                col1, col2 = st.columns(2)
                with col1:
                    if hasattr(jeu, 'Nombre_de_joueur') and pd.notna(jeu.Nombre_de_joueur):
                        st.markdown(f"🎲 **Joueurs**\n{format_player_count(jeu.Nombre_de_joueur)}")
                
                with col2:
                    if hasattr(jeu, 'temps_de_jeu') and pd.notna(jeu.temps_de_jeu):
                        st.markdown(f"⏱️ **Durée**\n{format_game_duration(jeu.temps_de_jeu)}")
                
               # Mécanisme sur toute la largeur
                if hasattr(jeu, 'mécanisme') and pd.notna(jeu.mécanisme):
                    st.markdown(f"⚙️ **Mécanisme**: {jeu.mécanisme}")
                
                # Bouton pour afficher l'avis
                if hasattr(jeu, 'avis') and pd.notna(jeu.avis):
                    if st.button(f"Voir l'avis - {jeu.Noms}", key=f"avis_{idx}"):
                        st.write(jeu.avis)

def main():
    setup_page()

    # Étape de chargement des données
    st.write("Chargement des données...")
    try:
        df = load_data()  # Charge les données depuis Google Sheets
        df_clean, validation_results = validate_and_clean_data(df)

        # Afficher les résultats de validation
        if validation_results:
            for result in validation_results:
                st.warning(result)

        # Création des filtres
        filters = create_filters(df_clean)

        # Filtrage des jeux
        jeux_filtres = filter_games(df_clean, filters)

        # Affichage des jeux
        st.write(f"### {len(jeux_filtres)} jeux trouvés")
        display_games_grid(jeux_filtres)

    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")

if __name__ == "__main__":
    main()
