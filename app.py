import pandas as pd
import streamlit as st
from typing import Optional, Tuple, List, Dict
import re

# Constante pour le lien Google Sheets
SHEET_ID = "1itKcj2L9HyA0GBIFcRTeQ8-OiIOI5eqw23-vvgXI5pQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# [All previous functions remain the same: validate_and_clean_data, format_game_duration, etc.]

def display_games_grid(jeux_filtres: pd.DataFrame, cols_per_row: int = 3):
    """Affiche les jeux en mode galerie avec des cartes plus visuelles"""
    cols = st.columns(cols_per_row)
    
    for idx, jeu in enumerate(jeux_filtres.itertuples()):
        with cols[idx % cols_per_row]:
            with st.container(border=True):  # Utilisation d'un conteneur avec bordure
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
