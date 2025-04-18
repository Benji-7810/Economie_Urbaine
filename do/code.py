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

# === Création du DataFrame CSP de base ===
csp_df = cadres[["Code", "Libellé"]].copy()

csp_df["cadres"] = pd.to_numeric(
    cadres["Part des cadres et prof. intellectuelles sup. dans le nb d’emplois au LT 2021"], errors='coerce')

csp_df["ouvriers"] = pd.to_numeric(
    ouvriers["Part des ouvriers dans le nb d’emplois au LT 2021"], errors='coerce')

csp_df["employes"] = pd.to_numeric(
    employes["Part des employés dans le nb d’emplois au LT 2021"], errors='coerce')

csp_df["artisans"] = pd.to_numeric(
    artisans["Part des artisans, commerçants, chefs d’ent. dans le nb d’emplois au LT 2021"], errors='coerce')

# === Fusion avec aires urbaines ===
csp_df = csp_df.rename(columns={"Code": "CODGEO"})
communes_au[["CODGEO", "AAV2020"]] = communes_au[["CODGEO", "AAV2020"]].astype(str)
csp_au = csp_df.merge(communes_au[["CODGEO", "AAV2020"]], on="CODGEO")

# Agrégation par AU
csp_au_grouped = csp_au.groupby("AAV2020")[["cadres", "ouvriers", "employes", "artisans"]].mean().reset_index()
csp_au_grouped["dissimilarite"] = abs(csp_au_grouped["cadres"] - csp_au_grouped["ouvriers"])

# Fusion avec logements sociaux
logements = logements.rename(columns={"GEO": "AAV2020", "nb_logements_sociaux": "logements_sociaux"})
logements["AAV2020"] = logements["AAV2020"].astype(str)
data = csp_au_grouped.merge(logements, on="AAV2020")

# Nettoyage des données
data_clean = data.copy()
data_clean = data_clean.dropna(subset=["logements_sociaux", "dissimilarite"])
data_clean = data_clean[data_clean["dissimilarite"] > 0]

if data_clean.empty:
    raise ValueError("⛔ Le DataFrame est vide après filtrage. Vérifie les données source.")

# Régression
X = sm.add_constant(data_clean["logements_sociaux"])
y = data_clean["dissimilarite"]
model = sm.OLS(y, X).fit()
print("📊 Résultats de la régression :")
print(model.summary())

# === Visualisation ===
plt.style.use('ggplot')
plt.figure(figsize=(10, 7))

plt.scatter(
    data_clean["logements_sociaux"],
    data_clean["dissimilarite"],
    s=50, alpha=0.6, edgecolor='k', linewidth=0.3,
    label="Aires urbaines"
)

plt.plot(
    data_clean["logements_sociaux"],
    model.predict(X),
    color='red', linestyle='--', linewidth=2,
    label="Régression linéaire"
)

plt.title("Corrélation entre logements sociaux et ségrégation socio-professionnelle", fontsize=15, weight='bold')
plt.xlabel("Nombre de logements sociaux (par aire urbaine)", fontsize=12)
plt.ylabel("Indice de dissimilarité (cadres vs ouvriers)", fontsize=12)
plt.xlim(0, data_clean["logements_sociaux"].quantile(0.98))
plt.ylim(0, data_clean["dissimilarite"].max() + 5)
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.legend()
plt.tight_layout()

# === Ajout des labels Paris, Lyon, Marseille ===
grandes_villes = {
    "Paris": "75056",
    "Lyon": "69123",
    "Marseille": "13055"
}

for ville, code_insee in grandes_villes.items():
    match = communes_au[communes_au["CODGEO"] == code_insee]
    if not match.empty:
        aav = match.iloc[0]["AAV2020"]
        point = data_clean[data_clean["AAV2020"] == str(aav)]
        if not point.empty:
            x = point["logements_sociaux"].values[0]
            y = point["dissimilarite"].values[0]
            plt.annotate(ville, (x, y), fontsize=11, weight='bold', color='black',
                         xytext=(5, 5), textcoords='offset points')

# Sauvegarde et affichage
plt.savefig("correlation_segregation_logements_ameliore.png", dpi=300)
plt.show()
