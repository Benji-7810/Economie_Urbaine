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

# Lecture des fichiers CSV
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

# Moyennes par AAV
moyennes = population_metier_df.groupby("AAV2020")["Indice_Homogeneite"].mean().reset_index()
moyennes["AAV2020"] = moyennes["AAV2020"].astype(str).str.zfill(3)
logements_sociaux_taux_df["AAV2020"] = logements_sociaux_taux_df["AAV2020"].astype(str).str.zfill(3)

# Fusion
df_result = moyennes.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
df_plot = df_result.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])

# Graphique
x = df_plot["PCT_SOCIAUX"] * 100
y = df_plot["Indice_Homogeneite"]
plt.figure(figsize=(10, 6))
plt.scatter(x, y, alpha=0.7, edgecolors='k', label="AAV")
m, b = np.polyfit(x, y, 1)
plt.plot(x, m * x + b, color="red", label=f"Tendance (r = {np.corrcoef(x, y)[0, 1]:.2f})")
plt.title("Corrélation : taux de logements sociaux vs ségrégation sociale")
plt.xlabel("Taux de logements sociaux (%)")
plt.ylabel("Indice d'homogénéité sociale (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_path, "correlation_logements_sociaux_segregation.png"))
plt.show()


# Fonction de préparation pour ajouter l’indice et fusionner avec le taux
def prepare_df(df_base, aav_list, taux_df):
    df = df_base[df_base["AAV2020"].isin(aav_list)].copy()
    df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)
    df = df.merge(taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
    return df.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])

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

    path = os.path.join(output_path, nom_fichier)
    plt.savefig(path)
    print(f"✅ Graphique sauvegardé : {path}")
    plt.show()

# Génération dynamique des top AAV
top_25_aav = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(25)["AAV2020"].tolist()
top_50_aav = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(50)["AAV2020"].tolist()
top_100_aav = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(100)["AAV2020"].tolist()
top_300_aav = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(300)["AAV2020"].tolist()
top_700_aav = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=False).head(700)["AAV2020"].tolist()
top_100_last = logements_sociaux_taux_df.sort_values(by="PCT_SOCIAUX", ascending=True).head(100)["AAV2020"].tolist()

# Tracés
tracer_graphique(prepare_df(population_metier_df, top_25_aav, logements_sociaux_taux_df),
                 "Top 25 taux les plus élevés", "blue", "graphique_top25_taux_sociaux.png")

tracer_graphique(prepare_df(population_metier_df, top_50_aav, logements_sociaux_taux_df),
                 "Top 50 taux les plus élevés", "green", "graphique_top50_taux_sociaux.png")

tracer_graphique(prepare_df(population_metier_df, top_100_aav, logements_sociaux_taux_df),
                 "Top 100 taux les plus élevés", "purple", "graphique_top100_taux_sociaux.png")

tracer_graphique(prepare_df(population_metier_df, top_300_aav, logements_sociaux_taux_df),
                 "Top 300 taux les plus élevés", "orange", "graphique_top300_taux_sociaux.png")

tracer_graphique(prepare_df(population_metier_df, top_700_aav, logements_sociaux_taux_df),
                 "Top 700 taux les plus élevés", "teal", "graphique_top700_taux_sociaux.png")

tracer_graphique(prepare_df(population_metier_df, top_100_last, logements_sociaux_taux_df),
                 "Top 100 taux les plus faibles", "red", "graphique_top100_faible_taux_sociaux.png")

# === GRAPHIQUES INDIVIDUELS PAR CSP ===
print("📊 Génération des graphiques individuels par catégorie socio-professionnelle...")

# Moyennes CSP par AAV
csp_moyennes = population_metier_df.groupby("AAV2020")[cols].mean().reset_index()
csp_moyennes["AAV2020"] = csp_moyennes["AAV2020"].astype(str).str.zfill(3)

# Fusion avec le taux de logements sociaux
df_csp = csp_moyennes.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
df_csp["PCT_SOCIAUX"] = df_csp["PCT_SOCIAUX"] * 100

# Titres explicites pour chaque CSP
titres_csp = {
    "CS2": "Artisans, commerçants, chefs d'entreprise",
    "CS3": "Cadres et professions intellectuelles supérieures",
    "CS5": "Employés",
    "CS6": "Ouvriers"
}

for col in cols:
    df_plot = df_csp.dropna(subset=["PCT_SOCIAUX", col])
    plt.figure(figsize=(10, 6))
    plt.scatter(df_plot["PCT_SOCIAUX"], df_plot[col], alpha=0.7, edgecolors='k', label=titres_csp[col])

    if len(df_plot) > 1:
        m, b = np.polyfit(df_plot["PCT_SOCIAUX"], df_plot[col], 1)
        r = np.corrcoef(df_plot["PCT_SOCIAUX"], df_plot[col])[0, 1]
        plt.plot(df_plot["PCT_SOCIAUX"], m * df_plot["PCT_SOCIAUX"] + b, color='red',
                 label=f'Tendance (r = {r:.2f})')

    plt.title(f"{titres_csp[col]} selon le taux de logements sociaux")
    plt.xlabel("Taux de logements sociaux (%)")
    plt.ylabel(titres_csp[col])
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    filename = f"{col}_vs_logements_sociaux.png"
    full_path = os.path.join(output_path, filename)
    plt.savefig(full_path)
    print(f"✅ Graphique sauvegardé : {full_path}")
    plt.show()
