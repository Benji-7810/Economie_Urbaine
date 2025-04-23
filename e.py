import pandas as pd
import numpy as np

# Charger le fichier CSV principal
df = pd.read_csv("population_metier.csv", delimiter=';')

# Renommer les colonnes de catégories sociales
df = df.rename(columns={
    "C21_ACTOCC1564_CS2": "CS2",
    "C21_ACTOCC1564_CS3": "CS3",
    "C21_ACTOCC1564_CS5": "CS5",
    "C21_ACTOCC1564_CS6": "CS6"
})

# Convertir les colonnes sociales en float
cols = ["CS2", "CS3", "CS5", "CS6"]
for col in cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Vérifier si la colonne AAV2020 existe
if "AAV2020" not in df.columns:
    # Ajouter AAV2020 via correspondance
    correspondance = pd.read_excel("table-appartenance-geo-communes-2024.xlsx", dtype={'CODGEO': str})
    correspondance["CODGEO"] = correspondance["CODGEO"].str.zfill(5)
    df["COM"] = df["COM"].astype(str).str.zfill(5)
    df = df.merge(correspondance[["CODGEO", "AAV2020"]], left_on="COM", right_on="CODGEO", how="left")
    df.drop(columns=["CODGEO"], inplace=True)

# Fonction d'indice d'homogénéité (entropie inversée)
def indice_homogeneite(row):
    total = row[cols].sum()
    if total == 0:
        return np.nan
    parts = row[cols] / total
    entropie = -np.sum([p * np.log(p) for p in parts if p > 0])
    indice = 1 - (entropie / np.log(len(cols)))
    return round(indice * 100, 2)  # format en pourcentage avec 2 décimales

# Appliquer à chaque ligne
df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)

# Moyenne par AAV
moyennes = df.groupby("AAV2020")["Indice_Homogeneite"].mean().reset_index()

# Arrondir à 2 décimales
moyennes["Indice_Homogeneite"] = moyennes["Indice_Homogeneite"].round(2)

# Export final
moyennes.to_csv("indice_homogeneite_par_AAV.csv", sep=';', index=False)

print("✅ Fichier généré : indice_homogeneite_par_AAV.csv avec valeurs en % et 2 décimales.")
