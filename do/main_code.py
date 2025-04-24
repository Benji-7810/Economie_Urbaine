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

# === GRAPHIQUES CSP COMBINÉS : CS2+CS3 et CS5+CS6 ===
print("📊 Génération des graphiques CSP combinées...")

# Calcul des combinaisons
population_metier_df["CS2_CS3"] = population_metier_df["CS2"] + population_metier_df["CS3"]
population_metier_df["CS5_CS6"] = population_metier_df["CS5"] + population_metier_df["CS6"]

# Moyennes par AAV
comb_cols = ["CS2_CS3", "CS5_CS6"]
csp_comb_moyennes = population_metier_df.groupby("AAV2020")[comb_cols].mean().reset_index()
csp_comb_moyennes["AAV2020"] = csp_comb_moyennes["AAV2020"].astype(str).str.zfill(3)

# Fusion avec le taux de logements sociaux
df_comb = pd.merge(csp_comb_moyennes, logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
df_comb["PCT_SOCIAUX"] = df_comb["PCT_SOCIAUX"] * 100

# Titres
titres_comb = {
    "CS2_CS3": "Artisans + Cadres (15-64 ans)",
    "CS5_CS6": "Employés + Ouvriers (15-64 ans)"
}

# Génération des graphiques
for col in comb_cols:
    plt.figure(figsize=(10, 6))
    plt.scatter(df_comb["PCT_SOCIAUX"], df_comb[col], alpha=0.7, edgecolors='k')

    m, b = np.polyfit(df_comb["PCT_SOCIAUX"], df_comb[col], 1)
    r = np.corrcoef(df_comb["PCT_SOCIAUX"], df_comb[col])[0, 1]
    plt.plot(df_comb["PCT_SOCIAUX"], m * df_comb["PCT_SOCIAUX"] + b, color='red', label=f'Tendance (r = {r:.2f})')

    plt.title(f"{titres_comb[col]} selon le taux de logements sociaux")
    plt.xlabel("Taux de logements sociaux (%)")
    plt.ylabel(titres_comb[col])
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    filename = f"{col}_vs_logements_sociaux.png"
    full_path = os.path.join(output_path, filename)
    plt.savefig(full_path)
    print(f"✅ Graphique sauvegardé : {full_path}")
    plt.show()


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


top_300_aav = [
    "347", "203", "82", "556", "545", "210", "341", "119", "295", "342",
    "375", "282", "278", "665", "378", "392", "63", "132", "18", "263", 
    "251", "563", "633", "536", "261", "257", "104", "232", "629", "624", 
    "212", "588", "286", "668", "277", "582", "249", "174", "159", "55", 
    "117", "489", "603", "436", "93", "9D4", "91", "44", "79", "169", 
    "12", "52", "108", "198", "57", "9B3", "109", "161", "510", "47", 
    "190", "516", "291", "671", "101", "571", "493", "352", "147", "240", 
    "332", "171", "187", "648", "610", "403", "415", "470", "336", "397", 
    "267", "308", "230", "252", "234", "590", "504", "338", "196", "49", 
    "428", "37", "356", "107", "9A2", "208", "5", "88", "185", "520", 
    "507", "346", "362", "66", "GEN", "191", "422", "585", "481", "494", 
    "565", "274", "32", "LUX", "193", "223", "423", "9D2", "328", "96", 
    "572", "LAU", "43", "122", "307", "554", "674", "623", "85", "487", 
    "51", "294", "102", "452", "491", "604", "326", "539", "142", "134", 
    "89", "46", "165", "433", "380", "524", "97", "482", "236", "62", 
    "304", "67", "552", "418", "300", "417", "640", "479", "627", "222", 
    "40", "70", "41", "138", "628", "151", "45", "613", "239", "678", 
    "596", "64", "28", "319", "201", "178", "9B2", "260", "262", "141", 
    "133", "534", "454", "9A1", "163", "177", "6", "182", "401", "22", 
    "450", "14", "172", "200", "SAR", "442", "424", "53", "273", "58", 
    "13", "8", "10", "135", "84", "562", "576", "426", "74", "318", 
    "280", "29", "20", "626", "3", "50", "658", "9D5", "75", "237", "372", 
    "125", "25", "9B1", "258", "118", "472", "476", "95", "157", "243", 
    "647", "270", "400", "484", "9C2", "620", "288", "94", "399", "505", 
    "116", "100", "34", "33", "80", "584", "595", "389", "358", "461", 
    "448", "164", "146", "167", "473", "150", "24", "652", "413", "162", 
    "35", "659", "86", "209", "299", "220", "78", "124", "2", "19", "23", 
    "69", "9C1", "61", "394", "643", "357", "264", "73", "480", "9D6", 
    "215", "176", "65", "83", "160", "364", "114", "197", "679", "619", 
    "265", "638", "561", "218", "136", "76", "130", "156", "242", "68", 
    "625", "26", "676", "287", "54", "90", "653", "183", "680", "4", "1", 
    "71", "586", "317", "630", "644", "128", "15", "216", "38", "374", 
    "77", "184", "144", "283", "9D1", "39", "660", "634", "581", "48", 
    "59", "9C3", "168", "303", "322", "36", "112", "508", "622", "221", 
    "560", "269", "42", "496", "409", "256", "512", "9D3"
]
# Filtrage des 100 premiers AAV
top_300_aav = population_metier_df[population_metier_df["AAV2020"].isin(top_300_aav)].copy()

# === Fonction de préparation ===
def prepare_df(df):
    df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)
    df = df.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
    return df.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])

# Préparation du DataFrame Top 100
top_300_aav = prepare_df(top_300_aav)

# === Graphique : Top 100 ===
plt.figure(figsize=(10, 6))
plt.scatter(top_300_aav["PCT_SOCIAUX"] * 100, top_300_aav["Indice_Homogeneite"],
            alpha=0.7, edgecolors='k', color='blue', label='Top 100 AAV')

if len(top_300_aav) > 1:
    x = top_300_aav["PCT_SOCIAUX"] * 100
    y = top_300_aav["Indice_Homogeneite"]
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m * x + b, color='darkblue', linestyle='--', label=f'Tendance (r = {np.corrcoef(x, y)[0,1]:.2f})')

plt.title("Homogénéité sociale pour les 350 AAV avec les taux les plus élevés de logements sociaux")
plt.xlabel("Taux de logements sociaux (%)")
plt.ylabel("Indice d'homogénéité sociale (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Sauvegarde
file_name = os.path.join(output_path, "graphique_top_350_logements_sociaux.png")
plt.savefig(file_name)
print(f"✅ Graphique 3 sauvegardé : {file_name}")
plt.show()


top_700_aav = [
    "618", "529", "CHA", "550", "523", "621", "537", "606", "669", "361",
    "464", "495", "528", "639", "354", "598", "578", "564", "681", "298",
    "386", "284", "384", "453", "526", "632", "414", "192", "9D7", "661",
    "538", "331", "502", "170", "231", "410", "131", "615", "355", "501",
    "271", "316", "302", "315", "455", "314", "506", "675", "549", "579",
    "542", "546", "377", "166", "425", "540", "497", "434", "599", "483",
    "492", "359", "657", "555", "245", "439", "340", "566", "266", "344",
    "371", "195", "477", "485", "567", "467", "673", "405", "616", "605",
    "312", "594", "600", "525", "363", "469", "471", "642", "527", "575",
    "233", "385", "255", "667", "382", "393", "431", "313", "180", "488",
    "601", "656", "353", "521", "334", "459", "9A3", "154", "396", "440",
    "139", "468", "460", "226", "444", "666", "253", "388", "430", "503",
    "682", "456", "631", "609", "569", "592", "645", "655", "531", "MON",
    "281", "408", "558", "517", "327", "532", "349", "323", "254", "366",
    "412", "533", "329", "296", "474", "391", "591", "515", "293", "369",
    "324", "390", "583", "541", "641", "339", "543", "103", "188", "325",
    "486", "92", "662", "404", "617", "646", "292", "199", "175", "509",
    "411", "654", "500", "677", "158", "290", "670", "519", "419", "597",
    "438", "651", "387", "127", "383", "421", "664", "368", "490", "241",
    "513", "518", "522", "143", "445", "650", "121", "113", "246", "181",
    "373", "568", "207", "129", "611", "551", "229", "202", "530", "548",
    "574", "219", "275", "376", "672", "106", "406", "173", "305", "614",
    "379", "547", "238", "306", "478", "309", "593", "463", "649", "98",
    "407", "635", "333", "335", "311", "447", "247", "301", "437", "381",
    "310", "636", "214", "360", "321", "514", "498", "398", "120", "577",
    "206", "458", "289", "235", "87", "115", "72", "395", "402", "443",
    "337", "570", "137", "544", "351", "462", "587", "370", "427", "350",
    "186", "348", "559", "320", "607", "105", "152", "279", "441", "60",
    "535", "250", "608", "225", "272", "345", "81", "365", "465", "259",
    "179", "330", "211", "475", "553", "228", "30", "511", "31", "451",
    "148", "149", "224", "111", "276", "449", "194", "557", "153", "17",
    "189", "217", "637", "227", "145", "285", "343", "663", "205", "297",
    "420", "612", "204", "580", "268", "213", "248", "BAL", "110", "416",
    "589", "367", "244", "429", "140", "466", "126", "155", "56", "432",
    "457", "573", "446", "123", "499", "602", "435", "347", "203", "82",
    "556", "545", "210", "341", "119", "295", "342", "375", "282", "278",
    "665", "378", "392", "63", "132", "18", "263", "251", "563", "633",
    "536", "261", "257", "104", "232", "629", "624", "212", "588", "286",
    "668", "277", "582", "249", "174", "159", "55", "117", "489", "603",
    "436", "93", "9D4", "91", "44", "79", "169", "12", "52", "108", "198",
    "57", "9B3", "109", "161", "510", "47", "190", "516", "291", "671",
    "101", "571", "493", "352", "147", "240", "332", "171", "187", "648",
    "610", "403", "415", "470", "336", "397", "267", "308", "230", "252",
    "234", "590", "504", "338", "196", "49", "428", "37", "356", "107",
    "9A2", "208", "5", "88", "185", "520", "507", "346", "362", "66", "GEN",
    "191", "422", "585", "481", "494", "565", "274", "32", "LUX", "193",
    "223", "423", "9D2", "328", "96", "572", "LAU", "43", "122", "307", "554",
    "674", "623", "85", "487", "51", "294", "102", "452", "491", "604", "326",
    "539", "142", "134", "89", "46", "165", "433", "380", "524", "97", "482",
    "236", "62", "304", "67", "552", "418", "300", "417", "640", "479", "627",
    "222", "40", "70", "41", "138", "628", "151", "45", "613", "239", "678",
    "596", "64", "28", "319", "201", "178", "9B2", "260", "262", "141", "133",
    "534", "454", "9A1", "163", "177", "6", "182", "401", "22", "450", "14",
    "172", "200", "SAR", "442", "424", "53", "273", "58", "13", "8", "10", "135",
    "84", "562", "576", "426", "74", "318", "280", "29", "20", "626", "3", "50",
    "658", "9D5", "75", "237", "372", "125", "25", "9B1", "258", "118", "472",
    "476", "95", "157", "243", "647", "270", "400", "484", "9C2", "620", "288",
    "94", "399", "505", "116", "100", "34", "33", "80", "584", "595", "389",
    "358", "461", "448", "164", "146", "167", "473", "150", "24", "652", "413",
    "162", "35", "659", "86", "209", "299", "220", "78", "124", "2", "19", "23",
    "69", "9C1", "61", "394", "643", "357", "264", "73", "480", "9D6", "215",
    "176", "65", "83", "160", "364", "114", "197", "679", "619", "265", "638",
    "561", "218", "136", "76", "130", "156", "242", "68", "625", "26", "676",
    "287", "54", "90", "653", "183", "680", "4", "1", "71", "586", "317", "630",
    "644", "128", "15", "216", "38", "374", "77", "184", "144", "283", "9D1",
    "39", "660", "634", "581", "48", "59", "9C3", "168", "303", "322", "36",
    "112", "508", "622", "221", "560", "269", "42", "496", "409", "256", "512",
    "9D3"
]

# Filtrage des 100 premiers AAV
top_700_aav = population_metier_df[population_metier_df["AAV2020"].isin(top_700_aav)].copy()

# === Fonction de préparation ===
def prepare_df(df):
    df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)
    df = df.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
    return df.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])

# Préparation du DataFrame Top 100
top_700_aav = prepare_df(top_700_aav)

# === Graphique : Top 100 ===
plt.figure(figsize=(10, 6))
plt.scatter(top_700_aav["PCT_SOCIAUX"] * 100, top_700_aav["Indice_Homogeneite"],
            alpha=0.7, edgecolors='k', color='blue', label='Top 100 AAV')

if len(top_300_aav) > 1:
    x = top_700_aav["PCT_SOCIAUX"] * 100
    y = top_700_aav["Indice_Homogeneite"]
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m * x + b, color='darkblue', linestyle='--', label=f'Tendance (r = {np.corrcoef(x, y)[0,1]:.2f})')

plt.title("Homogénéité sociale pour les 700 AAV avec les taux les plus élevés de logements sociaux")
plt.xlabel("Taux de logements sociaux (%)")
plt.ylabel("Indice d'homogénéité sociale (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Sauvegarde
file_name = os.path.join(output_path, "graphique_top_700_logements_sociaux.png")
plt.savefig(file_name)
print(f"✅ Graphique 3 sauvegardé : {file_name}")
plt.show()



top_100_last = [
    "618", "529", "550", "523", "621", "537", "606", "669", "361", "464", "495", "528", "639", "354",
    "598", "578", "564", "681", "298", "386", "284", "384", "453", "526", "632", "414", "192", "661",
    "538", "331", "502", "170", "231", "410", "131", "615", "355", "501", "271", "316", "302", "315",
    "455", "314", "506", "675", "549", "579", "542", "546", "377", "166", "425", "540", "497", "434",
    "599", "483", "492", "359", "657", "555", "245", "439", "340", "566", "266", "344", "371", "195",
    "477", "485", "567", "467", "673", "405", "616", "605", "312", "594", "600", "525", "363", "469",
    "471", "642", "527", "575", "233", "385", "255", "667", "382", "393", "431", "313", "180", "488"
]

# Filtrage des 100 premiers AAV
top_100_last = population_metier_df[population_metier_df["AAV2020"].isin(top_100_last)].copy()

# === Fonction de préparation ===
def prepare_df(df):
    df["Indice_Homogeneite"] = df.apply(indice_homogeneite, axis=1)
    df = df.merge(logements_sociaux_taux_df[["AAV2020", "PCT_SOCIAUX"]], on="AAV2020", how="left")
    return df.dropna(subset=["Indice_Homogeneite", "PCT_SOCIAUX"])

# Préparation du DataFrame Top 100
top_100_last = prepare_df(top_100_last)

# === Graphique : Top 100 ===
plt.figure(figsize=(10, 6))
plt.scatter(top_100_last["PCT_SOCIAUX"] * 100, top_100_last["Indice_Homogeneite"],
            alpha=0.7, edgecolors='k', color='blue', label='Top 100 AAV')

if len(top_100_last) > 1:
    x = top_100_last["PCT_SOCIAUX"] * 100
    y = top_100_last["Indice_Homogeneite"]
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m * x + b, color='darkblue', linestyle='--', label=f'Tendance (r = {np.corrcoef(x, y)[0,1]:.2f})')

plt.title("Homogénéité sociale pour les top_100_last avec les taux les plus élevés de logements sociaux")
plt.xlabel("Taux de logements sociaux (%)")
plt.ylabel("Indice d'homogénéité sociale (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Sauvegarde
file_name = os.path.join(output_path, "graphique_top_100_last_logements_sociaux.png")
plt.savefig(file_name)
print(f"✅ Graphique 3 sauvegardé : {file_name}")
plt.show()
