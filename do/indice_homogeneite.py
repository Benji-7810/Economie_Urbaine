import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Chargement des données
df = pd.read_csv("..\inputs\population_metier.csv", delimiter=';')

# Renommer les colonnes CSP
df = df.rename(columns={
    "C21_ACTOCC1564_CS2": "CS2",
    "C21_ACTOCC1564_CS3": "CS3",
    "C21_ACTOCC1564_CS5": "CS5",
    "C21_ACTOCC1564_CS6": "CS6"
})

# Conversion numérique
cols = ["CS2", "CS3", "CS5", "CS6"]
for col in cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Ajouter AAV2020 si manquant
if "AAV2020" not in df.columns:
    correspondance = pd.read_excel("table-appartenance-geo-communes-2024.xlsx", dtype={'CODGEO': str})
    correspondance["CODGEO"] = correspondance["CODGEO"].str.zfill(5)
    df["COM"] = df["COM"].astype(str).str.zfill(5)
    df = df.merge(correspondance[["CODGEO", "AAV2020"]], left_on="COM", right_on="CODGEO", how="left")
    df.drop(columns=["CODGEO"], inplace=True)

# Calcul de l'indice d'homogénéité
def indice_homogeneite(row):
    total = row[cols].sum()
    if total == 0:
        return np.nan
    parts = row[cols] / total
    entropie = -np.sum([p * np.log(p) for p in parts if p > 0])
    return round((1 - (entropie / np.log(len(cols)))) * 100, 2)

df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)

# Moyenne par AAV
moyennes = df.groupby("AAV2020")["Indice_Homogeneite"].mean().reset_index()

# Charger les taux de logements sociaux
df_logements = pd.read_csv("logements_sociaux_taux.csv", delimiter=';')
df_logements["AAV2020"] = df_logements["AAV2020"].astype(str).str.zfill(3)

# Fusion
moyennes["AAV2020"] = moyennes["AAV2020"].astype(str).str.zfill(3)
df_result = moyennes.merge(df_logements[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")

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
