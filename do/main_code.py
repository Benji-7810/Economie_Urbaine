# Importation des librairies
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("hello")

# Définition des chemins des fichiers
aire_urbaine = "../inputs/aire_urbaine.csv"
logements_sociaux_taux = "../inputs/logements_sociaux_taux.csv"
population_metier = "../inputs/population_metier.csv"
correspondance_excel = "table-appartenance-geo-aire_urbaines-2024.xlsx"
output_path = "../outputs/"
os.makedirs(output_path, exist_ok=True)

# Lecture des fichiers
aire_urbaine_df = pd.read_csv(aire_urbaine, sep=";")
logements_sociaux_taux_df = pd.read_csv(logements_sociaux_taux, sep=";")
population_metier_df = pd.read_csv(population_metier, sep=";")

# Conversion des colonnes CSP en numériques
cols = ["CS2", "CS3", "CS5", "CS6"]
for col in cols:
    population_metier_df[col] = pd.to_numeric(population_metier_df[col], errors="coerce")

# Ajout de la colonne AAV2020 si elle est manquante
if "AAV2020" not in population_metier_df.columns:
    correspondance = pd.read_excel(correspondance_excel, dtype={"CODGEO": str})
    correspondance["CODGEO"] = correspondance["CODGEO"].str.zfill(5)
    population_metier_df["COM"] = population_metier_df["COM"].astype(str).str.zfill(5)
    population_metier_df = population_metier_df.merge(
        correspondance[["CODGEO", "AAV2020"]],
        left_on="COM", right_on="CODGEO", how="left"
    ).drop(columns=["CODGEO"])

# Calcul de l'indice d'homogénéité
def indice_homogeneite(row):
    total = row[cols].sum()
    if total == 0:
        return np.nan
    parts = row[cols] / total
    entropie = -np.sum([p * np.log(p) for p in parts if p > 0])
    return round((1 - (entropie / np.log(len(cols)))) * 100, 2)

population_metier_df["Indice_Homogeneite"] = population_metier_df.apply(indice_homogeneite, axis=1)

# Fusion pour homogénéité par AAV
moyennes = population_metier_df.groupby("AAV2020")["Indice_Homogeneite"].mean().reset_index()
moyennes["AAV2020"] = moyennes["AAV2020"].astype(str).str.zfill(3)
logements_sociaux_taux_df["AAV2020"] = logements_sociaux_taux_df["AAV2020"].astype(str).str.zfill(3)
df_result = moyennes.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
df_plot = df_result.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])

# Fonction générique pour afficher et sauvegarder un graphique
def tracer_graphique(df, label, couleur, nom_fichier):
    x = df["PCT_SOCIAUX"] * 100
    y = df["Indice_Homogeneite"]
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, alpha=0.7, edgecolors='k', color=couleur, label=label)
    if len(df) > 1:
        m, b = np.polyfit(x, y, 1)
        r = np.corrcoef(x, y)[0, 1]
        plt.plot(x, m * x + b, color='darkblue', linestyle='--', label=f'Tendance (r = {r:.2f})')
    plt.title(f"Homogénéité sociale - {label}")
    plt.xlabel("Taux de logements sociaux (%)")
    plt.ylabel("Indice d'homogénéité sociale (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, nom_fichier))
    plt.show()

# Génération des top AAV
top_25 = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(25)["AAV2020"].tolist()
top_50 = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(50)["AAV2020"].tolist()
top_100 = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(100)["AAV2020"].tolist()
top_300 = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(300)["AAV2020"].tolist()
top_700 = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(700)["AAV2020"].tolist()
last_100 = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=True).head(100)["AAV2020"].tolist()
last_600 = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=True).head(600)["AAV2020"].tolist()

# Fonction de préparation des données
def prepare_df(df_base, aav_list):
    df = df_base[df_base["AAV2020"].isin(aav_list)].copy()
    df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)
    df = df.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
    return df.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])

# Tracés pour les top
tracer_graphique(prepare_df(population_metier_df, top_25), "Top 25", "blue", "top25.png")
tracer_graphique(prepare_df(population_metier_df, top_50), "Top 50", "green", "top50.png")
tracer_graphique(prepare_df(population_metier_df, top_100), "Top 100", "purple", "top100.png")
tracer_graphique(prepare_df(population_metier_df, top_300), "Top 300", "orange", "top300.png")
tracer_graphique(prepare_df(population_metier_df, top_700), "Top 700", "teal", "top700.png")
tracer_graphique(prepare_df(population_metier_df, last_100), "Bas 100", "red", "last100.png")
tracer_graphique(prepare_df(population_metier_df, last_600), "Bas 600", "red", "last600.png")

# === GRAPHIQUES CSP (individuels + combinés avec filtrage) ===
population_metier_df["CS2_CS3"] = population_metier_df["CS2"] + population_metier_df["CS3"]
population_metier_df["CS5_CS6"] = population_metier_df["CS5"] + population_metier_df["CS6"]

titres = {
    "CS2": "Artisans, commerçants, chefs d'entreprise",
    "CS3": "Cadres et professions intellectuelles supérieures",
    "CS5": "Employés",
    "CS6": "Ouvriers",
    "CS2_CS3": "Cadres + Chefs d'entreprise",
    "CS5_CS6": "Employés + Ouvriers"
}

def tracer_graphique_filtré(df_base, col, taux_df, titres, output_path):
    df = df_base.copy()
    df = df.merge(taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
    df = df.dropna(subset=[col, "PCT_SOCIAUX"])
    y_max = df[col].quantile(0.99)
    x_max = df["PCT_SOCIAUX"].quantile(0.99)
    df_filt = df[(df[col] < y_max) & (df["PCT_SOCIAUX"] < x_max)]
    x = df_filt["PCT_SOCIAUX"] * 100
    y = df_filt[col]
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, alpha=0.7, edgecolors='k', label=titres[col])
    if len(x) > 1:
        m, b = np.polyfit(x, y, 1)
        r = np.corrcoef(x, y)[0, 1]
        plt.plot(x, m * x + b, color='red', label=f'Tendance (r = {r:.2f})')
    plt.title(f"{titres[col]} selon le taux de logements sociaux")
    plt.xlabel("Taux de logements sociaux (%)")
    plt.ylabel(titres[col])
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    filename = f"{col}_vs_logements_sociaux.png"
    full_path = os.path.join(output_path, filename)
    plt.savefig(full_path)
    plt.show()

for col in ["CS2", "CS3", "CS5", "CS6", "CS2_CS3", "CS5_CS6"]:
    tracer_graphique_filtré(population_metier_df, col, logements_sociaux_taux_df, titres, output_path)
