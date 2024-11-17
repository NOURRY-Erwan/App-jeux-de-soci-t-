import pandas as pd
import streamlit as st
from typing import Optional
import re

def setup_page():
    """Configure la page Streamlit avec les paramètres initiaux."""
    st.set_page_config(
        page_title="Collection de Jeux de Société",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🎲 Ma Collection de Jeux de Société")

def extract_sheet_id(url: str) -> Optional[str]:
    """Extrait l'ID de la feuille Google Sheets depuis différents formats d'URL."""
    patterns = [
        r"/d/([a-zA-Z0-9-_]+)",  # Format standard
        r"id=([a-zA-Z0-9-_]+)",  # Format avec paramètre id
        r"spreadsheets/d/([a-zA-Z0-9-_]+)"  # Format long
    ]
    
    for pattern in patterns:
        if match := re.search(pattern, url):
            return match.group(1)
    return None

def load_data(sheet_url: str) -> pd.DataFrame:
    """Charge les données depuis Google Sheets avec gestion d'erreurs."""
    try:
        sheet_id = extract_sheet_id(sheet_url)
        if not sheet_id:
            raise ValueError("ID de feuille invalide")
        
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
        df = pd.read_csv(url)
        
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
        for col in ['récap', 'avis']:
            if col in df.columns:
                search_mask |= df[col].str.contains(search_text, case=False, na=False)
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

def display_game(jeu: pd.Series):
    """Affiche les détails d'un jeu dans un format amélioré."""
    # Création du titre avec la note si elle existe
    title = f"🎮 {jeu['Noms']}"
    if pd.notna(jeu.get('note')):
        title += f" ⭐ {jeu['note']}/5"
        
    with st.expander(title):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Affichage des images avec gestion d'erreurs
            for img_col in ['image', 'Boite de jeu']:
                if pd.notna(jeu[img_col]) and str(jeu[img_col]).startswith('http'):
                    try:
                        st.image(jeu[img_col], width=200)
                    except Exception:
                        st.warning(f"Impossible de charger l'image {img_col}")
        
        with col2:
            # Informations principales
            st.markdown("### 📊 Informations")
            infos = {
                "⏱️ Temps de jeu": jeu['temps de jeu'],
                "👥 Nombre de joueurs": jeu['Nombre de joueur'],
                "⚙️ Mécanisme": jeu['mécanisme']
            }
            
            for label, value in infos.items():
                if pd.notna(value):
                    st.write(f"**{label}** : {value}")
            
            # Récapitulatif
            if pd.notna(jeu.get('récap')):
                st.markdown("### 📝 Récapitulatif")
                st.write(jeu['récap'])
            
            # Avis
            if pd.notna(jeu.get('avis')):
                st.markdown("### 💭 Mon avis")
                st.write(jeu['avis'])
            
            # Lien vers les règles
            if pd.notna(jeu['Règles']) and str(jeu['Règles']).startswith('http'):
                st.link_button("📜 Voir les règles", jeu['Règles'])

def main():
    """Fonction principale de l'application."""
    setup_page()
    
    # Zone pour l'URL
    sheet_url = st.text_input(
        "Lien de partage Google Sheets",
        placeholder="Collez votre lien de partage ici..."
    )
    
    if sheet_url:
        # Chargement des données
        df = load_data(sheet_url)
        
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
        
        # Affichage de chaque jeu
        for _, jeu in jeux_filtres.iterrows():
            display_game(jeu)

if __name__ == "__main__":
    main()