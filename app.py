def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
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
        'Règles': str,
        'Boite_de_jeu': str
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
    
    # Vérification des URLs
    url_columns = ['Règles', 'Boite_de_jeu']
    for col in url_columns:
        if col in df_clean.columns:
            invalid_urls = df_clean[
                (df_clean[col].notna()) & 
                (~df_clean[col].str.startswith(('http://', 'https://')))
            ]
            if not invalid_urls.empty:
                validation_results.append(
                    f"URLs invalides dans {col}: {len(invalid_urls)} entrées"
                )
    
    return df_clean, validation_results

def format_game_duration(duration_str: str) -> str:
    """Formate la durée du jeu de manière cohérente."""
    try:
        # Extraction des nombres
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
def main():
    """Fonction principale de l'application."""
    setup_page()
    
    # Ajout du mode debug dans la sidebar
    with st.sidebar:
        st.divider()
        debug_mode = st.checkbox("🛠️ Mode Debug")
    
    # Chargement et validation des données
    df = load_data()
    df_clean, validation_results = validate_and_clean_data(df)
    
    if debug_mode:
        st.sidebar.expander("🔍 Informations de Debug").write({
            "Shape": df_clean.shape,
            "Colonnes": df_clean.columns.tolist(),
            "Types": df_clean.dtypes.to_dict(),
            "Valeurs manquantes": df_clean.isna().sum().to_dict()
        })
        
        if validation_results:
            st.sidebar.error("⚠️ Problèmes détectés:")
            for result in validation_results:
                st.sidebar.warning(result)
    
    # Création et application des filtres
    filters = create_filters(df_clean)
    jeux_filtres = filter_games(df_clean, filters)
    
    # Affichage des statistiques dans des colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Jeux trouvés", len(jeux_filtres))
    
    if 'note' in df_clean.columns:
        with col2:
            note_moyenne = jeux_filtres['note'].mean()
            if not pd.isna(note_moyenne):
                st.metric(
                    "⭐ Note moyenne",
                    f"{note_moyenne:.1f}/5",
                    delta=f"{(note_moyenne - df_clean['note'].mean()):.1f}"
                )
    
    with col3:
        jeux_notes = jeux_filtres['note'].notna().sum()
        total_jeux = len(jeux_filtres)
        if total_jeux > 0:
            st.metric(
                "📝 Jeux notés",
                f"{jeux_notes}/{total_jeux}",
                delta=f"{(jeux_notes/total_jeux*100):.0f}%"
            )
    
    with col4:
        duree_moyenne = jeux_filtres['temps_minutes'].mean()
        if not pd.isna(duree_moyenne):
            st.metric("⏱️ Durée moyenne", f"{duree_moyenne:.0f} min")
    
    # Affichage d'un résumé avant la grille
    if len(jeux_filtres) > 0:
        with st.expander("📈 Statistiques détaillées"):
            st.write("Top 5 des mécanismes les plus présents:")
            if 'mécanisme' in jeux_filtres.columns:
                mecanismes_counts = (
                    jeux_filtres['mécanisme']
                    .value_counts()
                    .head()
                    .to_dict()
                )
                for mec, count in mecanismes_counts.items():
                    st.write(f"- {mec}: {count} jeux")
    
    # Affichage en mode galerie
    display_games_grid(jeux_filtres)
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
