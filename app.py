
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
Normaliser les noms de colonnes
df_clean.columns = [col.strip().lower() for col in df_clean.columns]
Colonnes requises
required_columns = ['noms', 'temps_de_jeu', 'nombre_de_joueur', 'mécanisme', 'récap', 'note', 'image', 'règles']
Vérifier les colonnes manquantes
missing_columns = [col for col in required_columns if col not in df_clean.columns]
if missing_columns:
st.error(f"Colonnes manquantes : {', '.join(missing_columns)}")
return df_clean, [f"Colonnes manquantes : {', '.join(missing_columns)}"]
Conversion et nettoyage des types de données
df_clean['noms'] = df_clean['noms'].astype(str).str.strip()
df_clean['temps_de_jeu'] = df_clean['temps_de_jeu'].astype(str).str.strip()
df_clean['nombre_de_joueur'] = df_clean['nombre_de_joueur'].astype(str).str.strip()
df_clean['mécanisme'] = df_clean['mécanisme'].astype(str).str.strip()
df_clean['récap'] = df_clean['récap'].astype(str).str.strip()
Validation des notes
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
