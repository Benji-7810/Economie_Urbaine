# 🏙️ Analyse de l'Économie Urbaine : Logements Sociaux et Ségrégation

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data--Analysis-green)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange)
![Statistiques](https://img.shields.io/badge/Statistiques-INSEE-important)

---

## 📑 Table des matières

- [Contexte](#contexte)
- [Objectifs](#objectifs)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Arborescence](#arborescence)
- [Technologies utilisées](#technologies-utilisées)
- [Auteur](#auteur)

---

## 📖 Contexte

Ce projet a été réalisé dans le cadre d'une étude universitaire sur l'économie urbaine.  
L'objectif est d'analyser l'impact du taux de logements sociaux sur le niveau de ségrégation au sein des principales aires urbaines françaises.

Les données utilisées proviennent de bases publiques (INSEE) concernant :
- Les logements sociaux
- La population active par catégorie socio-professionnelle (CSP)
- Les indices d'homogénéité

---

## 🎯 Objectifs

- Calculer des indicateurs socio-économiques.
- Étudier la corrélation entre logement social et ségrégation.
- Générer des visualisations claires et interprétables.
- Produire une analyse écrite et une présentation.

---

## 📂 Structure du projet

Le projet est organisé comme suit :

```
Economie_Urbaine/
│
├── do/                # Scripts Python pour le traitement des données
│   ├── calcule_de_taux.py
│   ├── calcule_homogeneite.py
│   └── main_code.py
│
├── inputs/            # Données sources au format CSV
│   ├── aire_urbaine.csv
│   ├── Logement_Total.csv
│   ├── Logement_sociaux.csv
│   ├── logements_sociaux_taux.csv
│   ├── indice_homogeneite_et_taux_social_par_AAV.csv
│   └── population_metier.csv
│
├── outputs/           # Graphiques générés par les scripts
│   ├── correlation_logements_sociaux_segregation.png
│   ├── CS2_vs_logements_sociaux.png
│   ├── CS3_vs_logements_sociaux.png
│   ├── ... (autres graphiques)
│
├── Presentation.pdf   # Présentation visuelle du projet
├── texte_eco.docx     # Analyse économique rédigée
└── README.md          # Ce fichier
```

---

## ⚙️ Installation

Pour exécuter ce projet en local :

1. Cloner le dépôt GitHub :

```bash
git clone https://github.com/toncompte/Economie_Urbaine.git
cd Economie_Urbaine
```

2. Installer les dépendances nécessaires :

```bash
pip install pandas matplotlib
```

---

## 🚀 Utilisation

Pour lancer les analyses et générer les graphiques :

```bash
python do/main_code.py
```

Les résultats seront automatiquement enregistrés dans le dossier `outputs/`.

---

## 🛠️ Technologies utilisées

- **Python 3.10**
- **Pandas** — Analyse et manipulation de données
- **Matplotlib** — Visualisation de données
- **Données INSEE** — Sources statistiques officielles

---

