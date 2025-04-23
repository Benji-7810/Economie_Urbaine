#!/usr/bin/env python3
"""
Script Python pour calculer le pourcentage de logements sociaux par rapport aux logements totaux, par 'GEO'.
Usage :
    ./calc_pct.py logements_total_unique_COM.csv logement_sociaux.csv -o resultats.csv
"""

import csv
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Calcule le pourcentage de logements sociaux par rapport au total pour chaque GEO"
    )
    parser.add_argument('file_totals', help="Fichier CSV des logements totaux")
    parser.add_argument('file_sociaux', help="Fichier CSV des logements sociaux")
    parser.add_argument('-o', '--output', default='resultats.csv', help="Fichier CSV de sortie")
    return parser.parse_args()

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
    """
    results = []
    for geo, sociaux_val in sociaux.items():
        total_val = totals.get(geo)
        if total_val and total_val != 0:
            pct = round((sociaux_val / total_val) * 100, 2)
        else:
            pct = '?'
        results.append({'GEO': geo, 'LOG_SOCIAUX': sociaux_val, 'LOG_TOTAL': total_val, 'PCT_SOCIAUX': pct})
    return results

def write_output(results, output_path):
    """
    Écrit les résultats dans un fichier CSV.
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['GEO', 'LOG_SOCIAUX', 'LOG_TOTAL', 'PCT_SOCIAUX'], delimiter=';')
        writer.writeheader()
        for row in results:
            writer.writerow(row)

def main():
    args = parse_args()
    totals = read_values(args.file_totals)
    sociaux = read_values(args.file_sociaux)
    results = compute_percentages(totals, sociaux)
    write_output(results, args.output)
    print(f"Fichier de résultats généré : {args.output}")

if __name__ == '__main__':
    main()
