"""
Export des figures Uber Pickups vers reports/figures/
Usage : /opt/anaconda3/bin/python src/export_figures.py
"""
import glob
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "reports" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Chargement ─────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
files = sorted(glob.glob(str(DATA_DIR / "uber-raw-data-*14.csv")))

dfs = []
for f in files:
    tmp = pd.read_csv(f)
    tmp.columns = ['datetime', 'lat', 'lon', 'base']
    dfs.append(tmp)

df = pd.concat(dfs, ignore_index=True)
df['datetime'] = pd.to_datetime(df['datetime'])
df['hour']      = df['datetime'].dt.hour
df['dayofweek'] = df['datetime'].dt.dayofweek
df['dayname']   = df['datetime'].dt.day_name()

print(f"Dataset chargé : {len(df):,} pickups")

def save(fig, name):
    path = OUTPUT_DIR / f"{name}.png"
    fig.write_image(str(path))
    print(f"  {path.name}")

print("\nExport des figures Uber...")

# 01 — Pickups par heure
by_hour = df.groupby('hour').size().reset_index(name='pickups')
fig = px.bar(by_hour, x='hour', y='pickups',
             title='Nombre de pickups par heure de la journée',
             labels={'hour': 'Heure', 'pickups': 'Nombre de pickups'},
             color='pickups', color_continuous_scale='Blues')
save(fig, "01_pickups_by_hour")

# 02 — Pickups par jour
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_fr    = {'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
             'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi', 'Sunday': 'Dimanche'}

by_day = df.groupby('dayname').size().reset_index(name='pickups')
by_day['jour']  = by_day['dayname'].map(day_fr)
by_day['order'] = by_day['dayname'].map({d: i for i, d in enumerate(day_order)})
by_day = by_day.sort_values('order')

fig = px.bar(by_day, x='jour', y='pickups',
             title='Nombre de pickups par jour de la semaine',
             labels={'jour': 'Jour', 'pickups': 'Nombre de pickups'},
             color='pickups', color_continuous_scale='Purples')
save(fig, "02_pickups_by_day")

# 03 — Heatmap
heat = df.groupby(['dayofweek', 'hour']).size().reset_index(name='pickups')
heat_piv = heat.pivot(index='dayofweek', columns='hour', values='pickups')
heat_piv.index = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

fig = px.imshow(heat_piv,
                title='Heatmap — pickups par jour et heure',
                labels=dict(x='Heure', y='Jour', color='Pickups'),
                color_continuous_scale='YlOrRd',
                aspect='auto', width=900, height=400)
save(fig, "03_heatmap_day_hour")

# 04 — KMeans vendredi 18h
fri_6pm = df[(df['dayofweek'] == 4) & (df['hour'] == 18)].copy()
km_small = KMeans(n_clusters=8, random_state=42, n_init=10)
fri_6pm['cluster'] = km_small.fit_predict(fri_6pm[['lat', 'lon']].values).astype(str)

fig = px.scatter_mapbox(
    fri_6pm.sample(min(5000, len(fri_6pm)), random_state=42),
    lat='lat', lon='lon', color='cluster',
    mapbox_style='open-street-map', zoom=10,
    center={'lat': 40.73, 'lon': -73.99},
    title='KMeans (k=8) — Vendredi 18h',
    opacity=0.6, width=900, height=600
)
fig.update_traces(marker_size=5)
save(fig, "04_kmeans_friday_6pm")

# 05 — KMeans centres par jour
day_order_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_order_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

centers_list = []
for i, day in enumerate(day_order_en):
    data = df[df['dayname'] == day][['lat', 'lon']].dropna()
    km = KMeans(n_clusters=8, random_state=42, n_init=10)
    km.fit(data)
    c = pd.DataFrame(km.cluster_centers_, columns=['lat', 'lon'])
    c['jour'] = day_order_fr[i]
    centers_list.append(c)

centers_df = pd.concat(centers_list, ignore_index=True)
centers_df['taille'] = 1

fig = px.scatter_mapbox(
    centers_df, lat='lat', lon='lon',
    color='jour', size='taille', size_max=18,
    mapbox_style='open-street-map', zoom=10,
    center={'lat': 40.73, 'lon': -73.99},
    title='Zones chaudes par jour de la semaine — Centres KMeans (k=8)',
    width=900, height=600
)
save(fig, "05_kmeans_centers_by_day")

# 06 — DBSCAN
df_db = df.sample(50000, random_state=42).copy()
scaler = StandardScaler()
coords_scaled = scaler.fit_transform(df_db[['lat', 'lon']].values)

db = DBSCAN(eps=0.2, min_samples=100)
df_db['cluster'] = db.fit_predict(coords_scaled)

n_clusters = len(set(df_db['cluster'])) - (1 if -1 in df_db['cluster'].values else 0)
n_noise    = (df_db['cluster'] == -1).sum()
print(f"  DBSCAN : {n_clusters} clusters, {n_noise:,} points bruit")

df_db_clean = df_db[df_db['cluster'] != -1].copy()
df_db_clean['cluster'] = df_db_clean['cluster'].astype(str)

fig = px.scatter_mapbox(
    df_db_clean,
    lat='lat', lon='lon', color='cluster',
    mapbox_style='open-street-map', zoom=10,
    center={'lat': 40.73, 'lon': -73.99},
    title=f'DBSCAN — {n_clusters} clusters identifiés (points bruit exclus)',
    opacity=0.6, width=900, height=600
)
fig.update_traces(marker_size=5)
save(fig, "06_dbscan_clusters")

print(f"\nDone — 6 figures exportées dans {OUTPUT_DIR}")
