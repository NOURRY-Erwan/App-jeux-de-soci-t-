def display_games_grid(jeux_filtres: pd.DataFrame, cols_per_row: int = 3):
    """Affiche les jeux en mode galerie avec des cartes plus visuelles"""
    cols = st.columns(cols_per_row)
    
    for idx, jeu in enumerate(jeux_filtres.itertuples()):
        with cols[idx % cols_per_row]:
            with st.card():  # Utilisation d'une carte pour un cadre élégant
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
