# Analyse de la relation entre taux de logements sociaux et ségrégation socio-pro

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os

# === Détection du chemin absolu du dossier contenant le script ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "../input")

# Vérification des fichiers disponibles
print("Fichiers disponibles dans /input :", os.listdir(INPUT_DIR))

# === 1. Chargement des données ===
artisans = pd.read_csv(os.path.join(INPUT_DIR, "Part_des_artisans.csv"), sep=';')
cadres = pd.read_csv(os.path.join(INPUT_DIR, "Part_des_cadres.csv"), sep=';')
employes = pd.read_csv(os.path.join(INPUT_DIR, "Part_des_employés.csv"), sep=';')
ouvriers = pd.read_csv(os.path.join(INPUT_DIR, "Part_des_ouvriers.csv"), sep=';')
communes_au = pd.read_csv(os.path.join(INPUT_DIR, "base_communes_aires_urbaines.csv"), sep=',')
logements = pd.read_csv(os.path.join(INPUT_DIR, "logements_sociaux_epci_2021.csv"), sep=',')

print("✅ Tous les fichiers ont été chargés avec succès.")


# === 2. Fusion des parts CSP ===
csp_df = cadres[["Code", "Libellé"]].copy()
csp_df["cadres"] = pd.to_numeric(cadres.iloc[:, 2], errors='coerce')
csp_df["ouvriers"] = pd.to_numeric(ouvriers.iloc[:, 2], errors='coerce')
csp_df["employes"] = pd.to_numeric(employes.iloc[:, 2], errors='coerce')
csp_df["artisans"] = pd.to_numeric(artisans.iloc[:, 2], errors='coerce')

# === 3. Fusion avec les aires urbaines ===
communes_au[["CODGEO", "AAV2020"]] = communes_au[["CODGEO", "AAV2020"]].astype(str)
csp_df = csp_df.rename(columns={"Code": "CODGEO"})
csp_au = csp_df.merge(communes_au[["CODGEO", "AAV2020"]], on="CODGEO")

# === 4. Agrégation au niveau des aires urbaines ===
csp_au_grouped = csp_au.groupby("AAV2020")[["cadres", "ouvriers"]].mean().reset_index()

# === 5. Calcul d'un indice de dissimilarité simplifié (proxy) ===
csp_au_grouped["dissimilarite"] = abs(csp_au_grouped["cadres"] - csp_au_grouped["ouvriers"])

# === 6. Traitement du fichier logements sociaux ===
logements = logements.rename(columns={"GEO": "AAV2020", "nb_logements_sociaux": "logements_sociaux"})
logements["AAV2020"] = logements["AAV2020"].astype(str)

# === 7. Fusion avec logements sociaux ===
data = csp_au_grouped.merge(logements, on="AAV2020")

# === 8. Régression : taux logements sociaux vs ségrégation ===
X = sm.add_constant(data["logements_sociaux"])
y = data["dissimilarite"]
model = sm.OLS(y, X).fit()
print(model.summary())

# === 9. Graphique ===
plt.figure(figsize=(8,6))
plt.scatter(data["logements_sociaux"], data["dissimilarite"], alpha=0.7)
plt.plot(data["logements_sociaux"], model.predict(X), color='red', linestyle='--')
plt.xlabel("Taux de logements sociaux")
plt.ylabel("Indice de dissimilarité (cadres vs ouvriers)")
plt.title("Corrélation entre logements sociaux et ségrégation sociale")
plt.grid(True)
plt.tight_layout()
plt.savefig("correlation_segregation_logements.png")
plt.show()