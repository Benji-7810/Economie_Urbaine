#!/usr/bin/env python3
"""
Script Python pour calculer le pourcentage entre deux fichiers CSV sur la clé 'GEO'.
Usage:
    ./calc_pct.py fichier_totaux.csv fichier_sociaux.csv [-o output.csv]

- fichier_totaux.csv : CSV avec en-tête incluant 'GEO' et 'OBS_VALUE'.
- fichier_sociaux.csv : CSV avec en-tête incluant 'GEO' et 'OBS_VALUE'.
- output.csv : fichier de sortie, contiendra toutes les colonnes du second fichier plus une colonne 'PCT'.
  Si la valeur totale est manquante ou nulle, 'PCT' vaudra '?'.
"""
import csv
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calcule le pourcentage OBS_SOCIAUX / OBS_TOTAUX * 100 pour chaque GEO"
    )
    parser.add_argument(
        'file_totals',
        help="Chemin vers le fichier CSV des totaux (avec 'GEO' et 'OBS_VALUE')"
    )
    parser.add_argument(
        'file_sociaux',
        help="Chemin vers le fichier CSV des logements sociaux (avec 'GEO' et 'OBS_VALUE')"
    )
    parser.add_argument(
        '-o', '--output',
        default='output.csv',
        help="Chemin du fichier de sortie (par défaut 'output.csv')"
    )
    return parser.parse_args()


def read_totals(path):
    """
    Lit le fichier des totaux et renvoie un dict { GEO: valeur_totale }
    """
    totals = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
        try:
            idx_geo = header.index('GEO')
            idx_obs = header.index('OBS_VALUE')
        except ValueError as e:
            raise ValueError(f"En-tête invalide dans {path}, colonne manquante: {e}")

        for row in reader:
            geo = row[idx_geo]
            val = row[idx_obs].strip()
            try:
                totals[geo] = float(val)
            except ValueError:
                totals[geo] = None
    return totals


def process_files(totals, input_path, output_path):
    """
    Lit le fichier sociaux, calcule le pourcentage et écrit le résultat.
    """
    with open(input_path, newline='', encoding='utf-8') as fin, \
         open(output_path, 'w', newline='', encoding='utf-8') as fout:
        reader = csv.reader(fin, delimiter=';')
        writer = csv.writer(fout, delimiter=';')

        header = next(reader)
        writer.writerow(header + ['PCT'])

        # indices
        idx_geo = header.index('GEO')
        idx_obs = header.index('OBS_VALUE')

        for row in reader:
            geo = row[idx_geo]
            obs_val = row[idx_obs].strip()
            try:
                obs = float(obs_val)
            except ValueError:
                obs = None

            total = totals.get(geo)
            if total is None or total == 0 or obs is None:
                pct = '?'
            else:
                pct = f"{obs/total*100:.2f}"

            writer.writerow(row + [pct])


def main():
    args = parse_args()
    totals = read_totals(args.file_totals)
    process_files(totals, args.file_sociaux, args.output)
    print(f"Fichier de sortie généré : {args.output}")


if __name__ == '__main__':
    main()
