![Uber](Uber_logo.png)

# Uber Pickups — Zones chaudes à New York

Projet réalisé dans le cadre du bloc 3 de la certification CDSD (Jedha).

---

## Contexte

Uber constate que ses chauffeurs ne sont pas toujours au bon endroit au bon moment. Les utilisateurs n'acceptent pas d'attendre plus de 5 à 7 minutes — au-delà, ils annulent. L'idée : utiliser les données historiques de pickups pour identifier des zones chaudes et les recommander aux chauffeurs en temps réel.

---

## Ce que j'ai fait

- EDA des volumes de pickups par heure et par jour de la semaine
- **KMeans** : d'abord sur un créneau précis (vendredi 18h), puis généralisé à tous les jours
- **DBSCAN** : approche alternative basée sur la densité, sans fixer le nombre de clusters a priori
- Cartes interactives Plotly avec visualisation des clusters par jour/heure
- Comparaison des deux algorithmes

---

## Stack

- Python — Pandas, Plotly Express, Scikit-learn (KMeans, DBSCAN)

---

## Données

6 fichiers CSV couvrant avril à septembre 2014, ~4,5 millions de pickups à New York.
Colonnes : `Date/Time`, `Lat`, `Lon`, `Base`

---

## Structure

```
Uber/
├── data/
│   └── raw/               # CSV Uber 2014 (avr–sep)
├── docs/
│   └── 01-Uber_Pickups.ipynb
├── notebooks/
│   └── uber.ipynb
├── reports/
│   └── figures/
└── README.md
```

---

Julien CHARLIER — [(Github : Atomik31)](https://github.com/Atomik31)
