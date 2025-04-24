#!/usr/bin/env python3
"""
Script Python pour calculer le pourcentage de logements sociaux par rapport aux logements totaux, par 'GEO'.
"""

import csv

def read_values(path):
    """
    Lit un fichier CSV et retourne un dictionnaire { GEO: OBS_VALUE }.
    Ignore les lignes où OBS_VALUE est vide ou invalide.
    """
    values = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            geo = row.get('GEO')
            try:
                obs_value = float(row.get('OBS_VALUE', '').strip())
            except ValueError:
                obs_value = None
            if geo and obs_value is not None:
                values[geo] = obs_value
    return values

def compute_percentages(totals, sociaux):
    """
    Calcule les pourcentages de logements sociaux / logements totaux * 100
    et les trie par PCT_SOCIAUX de manière décroissante.
    """
    results = []
    for geo, sociaux_val in sociaux.items():
        total_val = totals.get(geo)
        if total_val and total_val != 0:
            pct = round((sociaux_val / total_val) * 100, 2)
        else:
            pct = '?'
        results.append({'GEO': geo, 'LOG_SOCIAUX': sociaux_val, 'LOG_TOTAL': total_val, 'PCT_SOCIAUX': pct})
    
    # Trier par PCT_SOCIAUX en ordre décroissant
    results_sorted = sorted(results, key=lambda x: x['PCT_SOCIAUX'], reverse=True)
    
    return results_sorted

def write_output(results, output_path):
    """
    Écrit les résultats dans un fichier CSV avec les entêtes modifiés.
    """
    # Modifier les en-têtes
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        # Nouveau nom de colonne pour GEO (AAV2020)
        fieldnames = ['AAV2020', 'LOG_SOCIAUX', 'LOG_TOTAL', 'PCT_SOCIAUX']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        # Écriture des résultats avec le champ 'AAV2020' à la place de 'GEO'
        for row in results:
            row['AAV2020'] = row.pop('GEO')  # Renommer la clé 'GEO' en 'AAV2020'
            writer.writerow(row)

def main():
    # Fichiers prédéfinis
    file_totals = "../inputs/Logement_Total.csv"
    file_sociaux = "../inputs/Logement_sociaux.csv"
    output_file = "../inputs/logements_sociaux_taux.csv"
    
    # Lecture des fichiers
    totals = read_values(file_totals)
    sociaux = read_values(file_sociaux)

    # Calcul des pourcentages
    results = compute_percentages(totals, sociaux)

    # Écriture du fichier de sortie avec entêtes modifiés
    write_output(results, output_file)
    print(f"✅ Fichier de résultats généré : {output_file}")

if __name__ == '__main__':
    main()
