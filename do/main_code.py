# Importation des librairies
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

print("hello")

# Définition des chemins absolus des fichiers CSV
commune = "../inputs/commune.csv"
logements_sociaux_taux = "../inputs/logements_sociaux_taux.csv"
population_metier = "../inputs/population_metier.csv"

# Lire les fichiers CSV en spécifiant le séparateur et sans sauter de lignes
try:
    commune_df = pd.read_csv(commune, sep=";", skiprows=0)
    logements_sociaux_taux_df = pd.read_csv(logements_sociaux_taux, sep=";", skiprows=0)
    population_metier_df = pd.read_csv(population_metier, sep=";", skiprows=0)
    print("Fichiers chargés avec succès.")
except Exception as e:
    print(f"Erreur lors de la lecture des fichiers: {e}")

# Affichage des premières lignes de chaque DataFrame
print("Commune :")
print(commune_df.head())

print("\nLogements Sociaux Taux :")
print(logements_sociaux_taux_df.head())

print("\nPopulation :")
print(population_metier_df.head())
