import pandas as pd
import numpy as np

# Charger le fichier CSV
df = pd.read_csv("population_metier.csv", delimiter=';')

# Renommer les colonnes
df = df.rename(columns={
    "C21_ACTOCC1564_CS2": "CS2",
    "C21_ACTOCC1564_CS3": "CS3",
    "C21_ACTOCC1564_CS5": "CS5",
    "C21_ACTOCC1564_CS6": "CS6"
})

# 🔧 Convertir les colonnes en float (au cas où elles sont en texte)
cols = ["CS2", "CS3", "CS5", "CS6"]
for col in cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Fonction d'indice d'homogénéité (entropie inversée)
def indice_homogeneite(row):
    total = row[cols].sum()
    if total == 0:
        return np.nan
    parts = row[cols] / total
    entropie = -np.sum([p * np.log(p) for p in parts if p > 0])
    return 1 - (entropie / np.log(len(cols)))  # normalisé

# Appliquer l'indice
df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)

# Regrouper par AAV
moyennes = df.groupby("AAV2020")["Indice_Homogeneite"].mean().reset_index()

# Sauvegarder
moyennes.to_csv("indice_homogeneite_par_AAV.csv", sep=';', index=False)

print("✅ Calcul terminé, fichier 'indice_homogeneite_par_AAV.csv' généré.")
