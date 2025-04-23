# Importation des librairies
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

print("hello")

# Définition des chemins absolus des fichiers CSV
commune = "../inputs/commune.csv"
logements_sociaux_taux = "../inputs/logements_sociaux_taux.csv"
population_metier = "../inputs/population_metier.csv"

# Lire les fichiers CSV en spécifiant le séparateur et sans sauter de lignes
try:
    commune_df = pd.read_csv(commune, sep=";", skiprows=0)
    logements_sociaux_taux_df = pd.read_csv(logements_sociaux_taux, sep=";", skiprows=0)
    population_metier_df = pd.read_csv(population_metier, sep=";", skiprows=0)
    print("Fichiers chargés avec succès.")
except Exception as e:
    print(f"Erreur lors de la lecture des fichiers: {e}")

# Affichage des premières lignes de chaque DataFrame
print("Commune :")
print(commune_df.head())

print("\nLogements Sociaux Taux :")
print(logements_sociaux_taux_df.head())

print("\nPopulation :")
print(population_metier_df.head())

# Traitement des données de population_metier_df
# Renommer les colonnes CSP
population_metier_df = population_metier_df.rename(columns={
    "C21_ACTOCC1564_CS2": "CS2",
    "C21_ACTOCC1564_CS3": "CS3",
    "C21_ACTOCC1564_CS5": "CS5",
    "C21_ACTOCC1564_CS6": "CS6"
})

# Conversion numérique
cols = ["CS2", "CS3", "CS5", "CS6"]
for col in cols:
    population_metier_df[col] = pd.to_numeric(population_metier_df[col], errors="coerce")

# Ajouter AAV2020 si manquant
if "AAV2020" not in population_metier_df.columns:
    correspondance = pd.read_excel("table-appartenance-geo-communes-2024.xlsx", dtype={'CODGEO': str})
    correspondance["CODGEO"] = correspondance["CODGEO"].str.zfill(5)
    population_metier_df["COM"] = population_metier_df["COM"].astype(str).str.zfill(5)
    population_metier_df = population_metier_df.merge(correspondance[["CODGEO", "AAV2020"]], left_on="COM", right_on="CODGEO", how="left")
    population_metier_df.drop(columns=["CODGEO"], inplace=True)

# Calcul de l'indice d'homogénéité
def indice_homogeneite(row):
    total = row[cols].sum()
    if total == 0:
        return np.nan
    parts = row[cols] / total
    entropie = -np.sum([p * np.log(p) for p in parts if p > 0])
    return round((1 - (entropie / np.log(len(cols)))) * 100, 2)

population_metier_df["Indice_Homogeneite"] = population_metier_df.apply(indice_homogeneite, axis=1)

# Moyenne par AAV
moyennes = population_metier_df.groupby("AAV2020")["Indice_Homogeneite"].mean().reset_index()

# Charger les taux de logements sociaux
logements_sociaux_taux_df["AAV2020"] = logements_sociaux_taux_df["AAV2020"].astype(str).str.zfill(3)

# Fusionner avec les moyennes d'indice d'homogénéité
moyennes["AAV2020"] = moyennes["AAV2020"].astype(str).str.zfill(3)
df_result = moyennes.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")

# Sauvegarder
df_result.to_csv("indice_homogeneite_et_taux_social_par_AAV.csv", sep=';', index=False)

print("✅ Fichier généré avec indice d’homogénéité + taux de logements sociaux.")

# Affichage graphique
df_plot = df_result.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])
x = df_plot["PCT_SOCIAUX"] * 100
y = df_plot["Indice_Homogeneite"]

plt.figure(figsize=(10, 6))
plt.scatter(x, y, alpha=0.7, edgecolors='k', label='AAV')
# Droite de régression
m, b = np.polyfit(x, y, 1)
plt.plot(x, m * x + b, color='red', label='Tendance')

plt.title("Corrélation : taux de logements sociaux vs ségrégation sociale")
plt.xlabel("Taux de logements sociaux (%)")
plt.ylabel("Indice d'homogénéité sociale (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
