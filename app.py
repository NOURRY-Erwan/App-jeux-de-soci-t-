import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuration de l'accès à Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('chemin/vers/votre/fichier_credentials.json', scope)
client = gspread.authorize(creds)

# Ouvrir le Google Sheet spécifié
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1itKcj2L9HyA0GBIFcRTeQ8-OiIOI5eqw23-vvgXI5pQ/edit?usp=sharing').worksheet('Feuille 1')

# Fonction pour charger les données
@st.cache_data
def load_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Interface utilisateur Streamlit
st.title('Gestionnaire de Jeux de Société')

# Charger les données
df = load_data()

# Système de filtres
st.sidebar.header('Filtres')
nombre_joueurs = st.sidebar.slider('Nombre de joueurs', 1, 20, (1, 20))
temps_de_jeu = st.sidebar.multiselect('Temps de jeu', df['temps_de_jeu'].unique())
mecanisme = st.sidebar.multiselect('Mécanisme', df['mécanisme'].unique())

# Appliquer les filtres
filtered_df = df[
    (df['Nombre_de_joueur'].str.split(' - ').str[0].astype(int) >= nombre_joueurs[0]) &
    (df['Nombre_de_joueur'].str.split(' - ').str[-1].astype(int) <= nombre_joueurs[1])
]

if temps_de_jeu:
    filtered_df = filtered_df[filtered_df['temps_de_jeu'].isin(temps_de_jeu)]
if mecanisme:
    filtered_df = filtered_df[filtered_df['mécanisme'].isin(mecanisme)]

# Affichage en galerie
st.header('Galerie des Jeux')
cols = st.columns(3)
for index, row in filtered_df.iterrows():
    with cols[index % 3]:
        st.image(row['image'], caption=row['Noms'], use_column_width=True)
        st.write(f"Joueurs : {row['Nombre_de_joueur']}")
        st.write(f"Temps : {row['temps_de_jeu']}")
        st.write(f"Mécanisme : {row['mécanisme']}")
        if st.button(f"Voir les règles de {row['Noms']}"):
            st.markdown(f"[Règles du jeu]({row['Règles']})")

# Recherche de jeux
st.header('Rechercher un jeu')
search_term = st.text_input('Entrez le nom du jeu')
if search_term:
    result = df[df['Noms'].str.contains(search_term, case=False)]
    st.dataframe(result[['Noms', 'temps_de_jeu', 'Nombre_de_joueur', 'mécanisme']])
