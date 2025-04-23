# Importation des librairies
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

print("hello")

# Définition des chemins absolus des fichiers CSV
aire_urbaine = "../inputs/aire_urbaine.csv"
logements_sociaux_taux = "../inputs/logements_sociaux_taux.csv"
population_metier = "../inputs/population_metier.csv"

# Lire les fichiers CSV en spécifiant le séparateur et sans sauter de lignes
try:
    aire_urbaine_df = pd.read_csv(aire_urbaine, sep=";", skiprows=0)
    logements_sociaux_taux_df = pd.read_csv(logements_sociaux_taux, sep=";", skiprows=0)
    population_metier_df = pd.read_csv(population_metier, sep=";", skiprows=0)
    print("Fichiers chargés avec succès.")
except Exception as e:
    print(f"Erreur lors de la lecture des fichiers: {e}")

# Affichage des premières lignes de chaque DataFrame
print("aire_urbaine :")
print(aire_urbaine_df.head())

print("\nLogements Sociaux Taux :")
print(logements_sociaux_taux_df.head())

print("\nPopulation :")
print(population_metier_df.head())

# Définir le répertoire de sortie
output_path = "../outputs/"
os.makedirs(output_path, exist_ok=True)  # Crée le répertoire si il n'existe pas

# Définir le répertoire de sortie pour la figure
output_path = "../outputs/"
os.makedirs(output_path, exist_ok=True)  # Crée le répertoire si il n'existe pas

# Conversion numérique
cols = ["CS2", "CS3", "CS5", "CS6"]
for col in cols:
    population_metier_df[col] = pd.to_numeric(population_metier_df[col], errors="coerce")

# Ajouter AAV2020 si manquant
if "AAV2020" not in population_metier_df.columns:
    correspondance = pd.read_excel("table-appartenance-geo-aire_urbaines-2024.xlsx", dtype={'CODGEO': str})
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

# Affichage graphique
df_plot = df_result.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])
x = df_plot["PCT_SOCIAUX"] * 100
y = df_plot["Indice_Homogeneite"]

# Création de la figure
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

# Sauvegarder la figure dans le répertoire outputs
output_image_path = os.path.join(output_path, "corrélation_logements_sociaux_segregation.png")
plt.savefig(output_image_path)
print(f"✅ Figure enregistrée dans {output_image_path}")

# Afficher la figure
plt.show()

# === GRAPHIQUES CSP : par catégorie sociale ===
print("📊 Génération des graphiques par CSP...")

# Titres explicites pour chaque catégorie
titres = {
    "CS2": "Artisans, commerçants, chefs d'entreprise (15-64 ans)",
    "CS3": "Cadres, professions intellectuelles supérieures (15-64 ans)",
    "CS5": "Employés (15-64 ans)",
    "CS6": "Ouvriers (15-64 ans)"
}

# Moyennes CSP par AAV
csp_moyennes = population_metier_df.groupby("AAV2020")[cols].mean().reset_index()
csp_moyennes["AAV2020"] = csp_moyennes["AAV2020"].astype(str).str.zfill(3)

# Fusion avec le taux de logements sociaux
df_corr = pd.merge(csp_moyennes, logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
df_corr["PCT_SOCIAUX"] = df_corr["PCT_SOCIAUX"] * 100

# Boucle sur chaque CSP
for col in cols:
    # Filtrage des extrêmes pour améliorer la lisibilité
    max_val = df_corr[col].quantile(0.99)
    df_filt = df_corr[df_corr[col] < max_val]

    plt.figure(figsize=(10, 6))
    plt.scatter(df_filt["PCT_SOCIAUX"], df_filt[col], alpha=0.7, edgecolors='k')

    # Droite de tendance
    m, b = np.polyfit(df_filt["PCT_SOCIAUX"], df_filt[col], 1)
    r = np.corrcoef(df_filt["PCT_SOCIAUX"], df_filt[col])[0, 1]
    plt.plot(df_filt["PCT_SOCIAUX"], m * df_filt["PCT_SOCIAUX"] + b, color='red', label=f'Tendance (r = {r:.2f})')

    # Titres et axes
    plt.title(f"{titres[col]} selon le taux de logements sociaux")
    plt.xlabel("Taux de logements sociaux (%)")
    plt.ylabel(titres[col])
    
    #plt.yticks(np.arange(0, max_val, 1000))

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Sauvegarde
    filename = f"{col}_vs_logements_sociaux.png"
    full_path = os.path.join(output_path, filename)
    plt.savefig(full_path)
    print(f"✅ Graphique sauvegardé : {full_path}")
    plt.show()


# Assure que les colonnes AAV2020 sont en chaînes de caractères
population_metier_df["AAV2020"] = population_metier_df["AAV2020"].astype(str)
logements_sociaux_taux_df["AAV2020"] = logements_sociaux_taux_df["AAV2020"].astype(str)

top_25_aav = [
    "9D3", "512", "256", "409", "496", "42", "269", "560", "221", "622", 
    "508", "112", "36", "322", "303", "168", "9C3", "59", "48", "581", 
    "634", "660", "39", "9D1", "283", "144"
]

df_top25 = population_metier_df[population_metier_df["AAV2020"].isin(top_25_aav)].copy()

# === Groupe 2 : tes 50 AAV (taux moyen + élevé) ===
aav_taux_moyen = [
    "242", "68", "625", "26", "676", "287", "54", "90", "653", "183", "680",
    "4", "1", "71", "586", "317", "630", "644", "128", "15", "216", "38", "374",
    "77", "184", "144", "283", "9D1", "39", "660", "634", "581", "48", "59",
    "9C3", "168", "303", "322", "36", "112", "508", "622", "221", "560", "269",
    "42", "496", "409", "256", "512", "9D3"
]
df_50 = population_metier_df[population_metier_df["AAV2020"].isin(aav_taux_moyen)].copy()

# === Fonction de préparation ===
def prepare_df(df):
    df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)
    df = df.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
    return df.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])

df_top25 = prepare_df(df_top25)
df_50 = prepare_df(df_50)

# === Graphique 1 : Top 25 ===
plt.figure(figsize=(10, 6))
plt.scatter(df_top25["PCT_SOCIAUX"] * 100, df_top25["Indice_Homogeneite"],
            alpha=0.7, edgecolors='k', color='blue', label='Top 25 taux les plus élevés')

if len(df_top25) > 1:
    x = df_top25["PCT_SOCIAUX"] * 100
    y = df_top25["Indice_Homogeneite"]
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m * x + b, color='darkblue', linestyle='--', label=f'Tendance (r = {np.corrcoef(x, y)[0,1]:.2f})')

plt.title("Homogénéité sociale - Top 25 taux de logements sociaux")
plt.xlabel("Taux de logements sociaux (%)")
plt.ylabel("Indice d'homogénéité sociale (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
file_25 = os.path.join(output_path, "graphique_top25_taux_sociaux.png")
plt.savefig(file_25)
print(f"✅ Graphique 1 sauvegardé : {file_25}")
plt.show()

# === Graphique 2 : Top 50 personnalisés ===
plt.figure(figsize=(10, 6))
plt.scatter(df_50["PCT_SOCIAUX"] * 100, df_50["Indice_Homogeneite"],
            alpha=0.7, edgecolors='k', color='darkgreen', label='50 AAV taux élevé/moyen')

if len(df_50) > 1:
    x = df_50["PCT_SOCIAUX"] * 100
    y = df_50["Indice_Homogeneite"]
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m * x + b, color='green', linestyle='--', label=f'Tendance (r = {np.corrcoef(x, y)[0,1]:.2f})')

plt.title("Homogénéité sociale - 50 AAV taux élevé ou moyen")
plt.xlabel("Taux de logements sociaux (%)")
plt.ylabel("Indice d'homogénéité sociale (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
file_50 = os.path.join(output_path, "graphique_top50_taux_sociaux.png")
plt.savefig(file_50)
print(f"✅ Graphique 2 sauvegardé : {file_50}")
plt.show()


# Assure que les colonnes AAV2020 sont en chaînes de caractères
population_metier_df["AAV2020"] = population_metier_df["AAV2020"].astype(str)
logements_sociaux_taux_df["AAV2020"] = logements_sociaux_taux_df["AAV2020"].astype(str)

# === Top 100 AAV ===
top_100_aav = [
    "9D3", "512", "256", "409", "496", "42", "269", "560", "221", "622",
    "508", "112", "36", "322", "303", "168", "9C3", "59", "48", "581", 
    "634", "660", "39", "9D1", "283", "144", "142", "284", "38", "149", 
    "75", "370", "104", "199", "50", "143", "61", "160", "179", "220", 
    "142", "250", "312", "444", "677", "67", "17", "178", "360", "300", 
    "115", "125", "161", "300", "242", "54", "68", "152", "201", "389", 
    "456", "508", "213", "360", "487", "313", "343", "317", "176", "290", 
    "76", "204", "136", "275", "442", "407", "166", "249", "295", "341", 
    "470", "322", "241", "48", "482", "144", "170", "103", "223", "368", 
    "224", "298", "101", "255", "265", "474", "317", "395", "72", "252", 
    "306", "59", "21", "48", "532", "233", "234", "84", "290", "295", 
    "274", "312", "285", "181", "69", "35", "451", "238", "272"
]

# Filtrage des 100 premiers AAV
df_top_100 = population_metier_df[population_metier_df["AAV2020"].isin(top_100_aav)].copy()

# === Fonction de préparation ===
def prepare_df(df):
    df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)
    df = df.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
    return df.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])

# Préparation du DataFrame Top 100
df_top_100 = prepare_df(df_top_100)

# === Graphique : Top 100 ===
plt.figure(figsize=(10, 6))
plt.scatter(df_top_100["PCT_SOCIAUX"] * 100, df_top_100["Indice_Homogeneite"],
            alpha=0.7, edgecolors='k', color='blue', label='Top 100 AAV')

if len(df_top_100) > 1:
    x = df_top_100["PCT_SOCIAUX"] * 100
    y = df_top_100["Indice_Homogeneite"]
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m * x + b, color='darkblue', linestyle='--', label=f'Tendance (r = {np.corrcoef(x, y)[0,1]:.2f})')

plt.title("Homogénéité sociale pour les 100 AAV avec les taux les plus élevés de logements sociaux")
plt.xlabel("Taux de logements sociaux (%)")
plt.ylabel("Indice d'homogénéité sociale (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Sauvegarde
file_name = os.path.join(output_path, "graphique_top_100_logements_sociaux.png")
plt.savefig(file_name)
print(f"✅ Graphique 3 sauvegardé : {file_name}")
plt.show()
