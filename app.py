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
