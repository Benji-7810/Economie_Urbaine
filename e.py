import pandas as pd
import numpy as np

# Chargement des données principales
df = pd.read_csv("population_metier.csv", delimiter=';')

# Renommer les colonnes des catégories sociales
df = df.rename(columns={
    "C21_ACTOCC1564_CS2": "CS2",
    "C21_ACTOCC1564_CS3": "CS3",
    "C21_ACTOCC1564_CS5": "CS5",
    "C21_ACTOCC1564_CS6": "CS6"
})

# Conversion en numérique
cols = ["CS2", "CS3", "CS5", "CS6"]
for col in cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Fonction d’indice d’homogénéité (entropie inversée)
def indice_homogeneite(row):
    total = row[cols].sum()
    if total == 0:
        return np.nan
    parts = row[cols] / total
    entropie = -np.sum([p * np.log(p) for p in parts if p > 0])
    return round((1 - (entropie / np.log(len(cols)))) * 100, 2)  # % à 2 décimales

# Calculer l'indice
df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)

# Moyenne par AAV2020
moyennes = df.groupby("AAV2020")["Indice_Homogeneite"].mean().reset_index()
moyennes["Indice_Homogeneite"] = moyennes["Indice_Homogeneite"].round(2)

# Charger les taux de logements sociaux
df_logements = pd.read_csv("logements_sociaux_taux.csv", delimiter=';')
df_logements["AAV2020"] = df_logements["AAV2020"].astype(str).str.zfill(3)

# Fusion avec les taux
moyennes["AAV2020"] = moyennes["AAV2020"].astype(str).str.zfill(3)
resultat = moyennes.merge(df_logements[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")

# Export final
resultat.to_csv("indice_homogeneite_et_taux_social_par_AAV.csv", sep=';', index=False)

print("✅ Fichier généré avec indice d’homogénéité + taux de logements sociaux.")
