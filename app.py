import pandas as pd
import streamlit as st
from typing import Optional
import re

# Constante pour le lien Google Sheets
SHEET_ID = 1itKcj2L9HyA0GBIFcRTeQ8-OiIOI5eqw23-vvgXI5pQ  # L'ID se trouve dans l'URL entre /d/ et /edit
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def load_data() -> pd.DataFrame:
    """Charge les données depuis Google Sheets."""
    try:
        df = pd.read_csv(SHEET_URL)
        
        # Conversion de la colonne note en numérique
        if 'note' in df.columns:
            df['note'] = pd.to_numeric(df['note'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        st.write("URL utilisée:", SHEET_URL)  # Pour debug
        st.stop()

def setup_page():
    """Configure la page Streamlit avec les paramètres initiaux."""
    st.set_page_config(
        page_title="Collection de Jeux de Société",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🎲 Ma Collection de Jeux de Société")

def load_data() -> pd.DataFrame:
    """Charge les données depuis Google Sheets."""
    try:
        df = pd.read_csv(SHEET_URL)
        
        # Conversion de la colonne note en numérique
        if 'note' in df.columns:
            df['note'] = pd.to_numeric(df['note'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
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
        
        # Filtre par nombre de joueurs avec min/max
        st.subheader("👥 Nombre de joueurs")
        col1, col2 = st.columns(2)
        with col1:
            min_joueurs = st.number_input("Min", min_value=1, max_value=10, value=1)
        with col2:
            max_joueurs = st.number_input("Max", min_value=1, max_value=10, value=4)
        
        # Filtre par temps de jeu avec range slider
        st.subheader("⏱️ Temps de jeu")
        temps_range = st.slider(
            "Durée (minutes)",
            min_value=0,
            max_value=180,
            value=(0, 120),
            step=15
        )
        
        # Filtre par mécanisme avec recherche
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
    """Applique les filtres sur le DataFrame."""
    min_joueurs, max_joueurs, temps_range, mecanismes, search_text, note_min, tri = filters
    
    # Fonction pour extraire les nombres d'une chaîne
    def extract_numbers(text):
        if pd.isna(text):
            return []
        return [int(num) for num in re.findall(r'\d+', str(text))]
    
    # Application des filtres
    mask = pd.Series(True, index=df.index)
    
    # Filtre note minimum
    if 'note' in df.columns:
        mask &= df['note'] >= note_min
    
    # Filtre nombre de joueurs
    df['nombres_joueurs'] = df['Nombre de joueur'].apply(extract_numbers)
    mask &= df['nombres_joueurs'].apply(
        lambda x: any(min_joueurs <= n <= max_joueurs for n in x)
    )
    
    # Filtre temps de jeu
    df['temps_minutes'] = df['temps de jeu'].apply(
        lambda x: extract_numbers(str(x))[0] if extract_numbers(str(x)) else 0
    )
    mask &= df['temps_minutes'].between(temps_range[0], temps_range[1])
    
    # Filtre mécanismes
    if mecanismes:
        mask &= df['mécanisme'].isin(mecanismes)
    
    # Filtre texte
    if search_text:
        search_mask = df['Noms'].str.contains(search_text, case=False, na=False)
        if 'avis' in df.columns:
            search_mask |= df['avis'].str.contains(search_text, case=False, na=False)
        mask &= search_mask
    
    filtered_df = df[mask]
    
    # Application du tri
    if tri == "nom_asc":
        filtered_df = filtered_df.sort_values('Noms')
    elif tri == "nom_desc":
        filtered_df = filtered_df.sort_values('Noms', ascending=False)
    elif tri == "note_asc" and 'note' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('note')
    elif tri == "note_desc" and 'note' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('note', ascending=False)
    
    return filtered_df

def display_games_grid(jeux_filtres: pd.DataFrame, cols_per_row: int = 3):
    """Affiche les jeux en mode galerie."""
    # Création des colonnes pour la grille
    cols = st.columns(cols_per_row)
    
    # Parcours des jeux et affichage dans la grille
    for idx, jeu in enumerate(jeux_filtres.itertuples()):
        with cols[idx % cols_per_row]:
            # Container pour le jeu
            with st.container():
                # Image du jeu
                if hasattr(jeu, 'image') and pd.notna(jeu.image) and str(jeu.image).startswith('http'):
                    st.image(jeu.image, use_column_width=True)
                elif hasattr(jeu, 'Boite_de_jeu') and pd.notna(jeu.Boite_de_jeu) and str(jeu.Boite_de_jeu).startswith('http'):
                    st.image(jeu.Boite_de_jeu, use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/200x200?text=Pas+d'image", use_column_width=True)
                
                # Titre et note
                title = f"### {jeu.Noms}"
                if hasattr(jeu, 'note') and pd.notna(jeu.note):
                    title += f" ⭐ {jeu.note}/5"
                st.markdown(title)
                
                # Informations principales
                st.write(f"🎲 **Joueurs**: {jeu.Nombre_de_joueur}")
                st.write(f"⏱️ **Durée**: {jeu.temps_de_jeu}")
                if hasattr(jeu, 'mécanisme') and pd.notna(jeu.mécanisme):
                    st.write(f"⚙️ **Mécanisme**: {jeu.mécanisme}")
                
                # Avis (si présent)
                if hasattr(jeu, 'avis') and pd.notna(jeu.avis):
                    with st.expander("💭 Mon avis"):
                        st.write(jeu.avis)
                
                # Lien vers les règles
                if hasattr(jeu, 'Règles') and pd.notna(jeu.Règles) and str(jeu.Règles).startswith('http'):
                    st.link_button("📜 Règles", jeu.Règles)

def main():
    """Fonction principale de l'application."""
    setup_page()
    
    # Chargement des données
    df = load_data()
    
    # Création et application des filtres
    filters = create_filters(df)
    jeux_filtres = filter_games(df, filters)
    
    # Affichage des statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Nombre de jeux trouvés", len(jeux_filtres))
    if 'note' in df.columns:
        with col2:
            note_moyenne = jeux_filtres['note'].mean()
            if not pd.isna(note_moyenne):
                st.metric("⭐ Note moyenne", f"{note_moyenne:.1f}/5")
        with col3:
            jeux_notes = jeux_filtres['note'].notna().sum()
            st.metric("📝 Jeux notés", f"{jeux_notes}/{len(jeux_filtres)}")
    
    # Affichage en mode galerie
    display_games_grid(jeux_filtres)

if __name__ == "__main__":
    main()
