# Analyse de la relation entre taux de logements sociaux et ségrégation socio-pro

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# === Détection du chemin absolu ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "../input")

print("Fichiers disponibles dans /input :", os.listdir(INPUT_DIR))

# === Chargement des fichiers CSV ===
cadres = pd.read_csv(os.path.join(INPUT_DIR, "Part_des_cadres.csv"), sep=';')
ouvriers = pd.read_csv(os.path.join(INPUT_DIR, "Part_des_ouvriers.csv"), sep=';')
employes = pd.read_csv(os.path.join(INPUT_DIR, "Part_des_employés.csv"), sep=';')
artisans = pd.read_csv(os.path.join(INPUT_DIR, "Part_des_artisans.csv"), sep=';')
communes_au = pd.read_csv(os.path.join(INPUT_DIR, "base_communes_aires_urbaines.csv"), sep=',')
logements = pd.read_csv(os.path.join(INPUT_DIR, "logements_sociaux_epci_2021.csv"), sep=',')

print("✅ Tous les fichiers ont été chargés avec succès.")

# === Nettoyage et renommage des colonnes utiles ===

# On extrait et renomme uniquement les colonnes nécessaires pour chaque CSP
cadres = cadres.rename(columns={
    "Code": "CODGEO",
    "Part des cadres et prof. intellectuelles sup. dans le nb d’emplois au LT 2021": "cadres"
})[["CODGEO", "cadres"]]

ouvriers = ouvriers.rename(columns={
    "Code": "CODGEO",
    "Part des ouvriers dans le nb d’emplois au LT 2021": "ouvriers"
})[["CODGEO", "ouvriers"]]

employes = employes.rename(columns={
    "Code": "CODGEO",
    "Part des employés dans le nb d’emplois au LT 2021": "employes"
})[["CODGEO", "employes"]]

artisans = artisans.rename(columns={
    "Code": "CODGEO",
    "Part des artisans, commerçants, chefs d’ent. dans le nb d’emplois au LT 2021": "artisans"
})[["CODGEO", "artisans"]]

# Conversion des colonnes en float (au cas où certaines sont mal lues)
for df in [cadres, ouvriers, employes, artisans]:
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# === Fusion des CSP sur le code commune ===
csp_df = cadres.merge(ouvriers, on="CODGEO", how="outer") \
               .merge(employes, on="CODGEO", how="outer") \
               .merge(artisans, on="CODGEO", how="outer")

# === Nettoyage du fichier des communes (aires urbaines) ===
communes_au = communes_au[["CODGEO", "AAV2020", "LIBAAV2020"]].astype(str)
csp_df["CODGEO"] = csp_df["CODGEO"].astype(str)

# === Fusion avec aires urbaines ===
csp_df = csp_df.merge(communes_au, on="CODGEO", how="left")

# === Agrégation des données par aire urbaine ===
csp_au = csp_df.groupby(["AAV2020", "LIBAAV2020"])[["cadres", "ouvriers", "employes", "artisans"]].mean().reset_index()

# === Calcul de l'indice de dissimilarité (cadres vs ouvriers) ===
csp_au["dissimilarite"] = abs(csp_au["cadres"] - csp_au["ouvriers"])

# === Nettoyage des données logements sociaux ===
logements = logements.rename(columns={"GEO": "AAV2020", "nb_logements_sociaux": "logements_sociaux"})
logements["AAV2020"] = logements["AAV2020"].astype(str)

# === Fusion finale CSP + logements sociaux ===
data = csp_au.merge(logements, on="AAV2020", how="left")
data = data.dropna(subset=["logements_sociaux", "dissimilarite"])

print("📂 Données prêtes pour l’analyse.")
print(data.head(10))  # Affiche les 10 premières lignes


# === Étape 1 : Top 20 AU avec le plus de logements sociaux ===
top_20 = data.sort_values("logements_sociaux", ascending=False).head(20)

plt.figure(figsize=(12, 7))
plt.barh(top_20["LIBAAV2020"], top_20["logements_sociaux"], color='skyblue')
plt.xlabel("Nombre de logements sociaux")
plt.title("Top 20 des aires urbaines avec le plus de logements sociaux")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("graphique_1_logements_sociaux.png", dpi=300)
plt.show()

# === Étape 2 : Dissimilarité pour ces mêmes AU ===
plt.figure(figsize=(12, 7))
plt.barh(top_20["LIBAAV2020"], top_20["dissimilarite"], color='coral')
plt.xlabel("Indice de dissimilarité (cadres vs ouvriers)")
plt.title("Ségrégation socio-pro dans les AU les plus dotées en logements sociaux")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("graphique_2_dissimilarite.png", dpi=300)
plt.show()

# === Étape 3 : Corrélation + régression ===
X = sm.add_constant(data["logements_sociaux"])
y = data["dissimilarite"]
model = sm.OLS(y, X).fit()

print("📈 Résultats de la régression linéaire :")
print(model.summary())

plt.figure(figsize=(10, 7))
plt.scatter(data["logements_sociaux"], data["dissimilarite"], s=50, alpha=0.6, edgecolor='k', linewidth=0.5)
plt.plot(data["logements_sociaux"], model.predict(X), color='red', linestyle='--', linewidth=2, label="Régression linéaire")

plt.title("Corrélation entre logements sociaux et ségrégation socio-professionnelle", fontsize=14, weight='bold')
plt.xlabel("Nombre de logements sociaux par aire urbaine", fontsize=12)
plt.ylabel("Indice de dissimilarité (cadres vs ouvriers)", fontsize=12)
plt.xlim(0, data["logements_sociaux"].quantile(0.98))
plt.ylim(0, data["dissimilarite"].max() + 5)
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.legend()
plt.tight_layout()
plt.savefig("graphique_3_regression.png", dpi=300)
plt.show()