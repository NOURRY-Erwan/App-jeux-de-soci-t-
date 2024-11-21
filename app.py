import pandas as pd
import streamlit as st
from typing import Optional, Tuple, List
import re  # Importation de la bibliothèque regex
Constante pour le lien Google Sheets
SHEET_ID = "1itKcj2L9HyA0GBIFcRTeQ8-OiIOI5eqw23-vvgXI5pQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
def validate_and_clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
"""Valide et nettoie les données du DataFrame."""
Copie du DataFrame pour éviter les modifications sur l'original
df_clean = df.copy()
Nettoyage des noms de colonnes
df_clean.columns = df_clean.columns.str.strip()
Mapping des types de données attendus
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
Conversion et nettoyage des colonnes
for col, dtype in column_types.items():
if col in df_clean.columns:
try:
if dtype == str:
df_clean[col] = df_clean[col].astype(str).replace('nan', '').str.strip()
elif dtype == float:
df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
except Exception as e:
st.warning(f"Erreur lors de la conversion de la colonne {col}: {str(e)}")
Validation des données
validation_results = []
Vérification des valeurs de notes
if 'Note' in df_clean.columns:
invalid_notes = df_clean[
(df_clean['Note'].notna()) &
((df_clean['Note'] < 0) | (df_clean['Note'] > 5))
]
if not invalid_notes.empty:
validation_results.append(
f"Notes invalides détectées: {len(invalid_notes)} entrées hors de la plage 0-5"
)
Vérification des URLs pour Règles (PDF links)
url_columns = ['Règles']
for col in url_columns:
if col in df_clean.columns:
invalid_urls = df_clean[
(df_clean[col].notna()) &
(~df_clean[col].str.contains(r'https?://.*.pdf$', regex=True, na=False))
]
if not invalid_urls.empty:
validation_results.append(
f"URLs invalides dans {col}: {len(invalid_urls)} entrées qui ne sont pas des liens PDF"
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
/* Style pour les cartes de jeux /
.stExpander {
background-color: #f8f9fa;
border-radius: 10px;
border: 1px solid #dee2e6;
margin-bottom: 1rem;
}/ Style pour les métriques /
.stMetric {
background-color: white;
padding: 1rem;
border-radius: 10px;
box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}/ Style pour les images /
.stImage {
border-radius: 10px;
box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}/ Style pour les titres des jeux /
h3 {
margin-top: 0.5rem !important;
margin-bottom: 0.5rem !important;
}/ Style pour les boutons */
.stButton > button {
width: 100%;
border-radius: 20px;
margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)
