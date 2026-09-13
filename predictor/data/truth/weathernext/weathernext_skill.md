# WeatherNext 3 : mesure (ou blocage)

Généré : 2026-09-12T18:07:27Z. Fenêtre Open-Meteo demandée 2026-09-08 → 2026-09-12.
Nom stable du levier : WeatherNext 3.
Verdict : pas encore mesurable (bloquée).

Le champion en ligne n'est pas changé. Le site public n'est pas changé.
Pas de pari avec de l'argent réel. Aucun chiffre manquant n'a été inventé.

## WeatherNext 3

Bloquée. Rien n'a été noté avec ce modèle.

- Open-Meteo refuse tous les noms WeatherNext 3 essayés (google_weathernext3_ensemble, google_weathernext_3, google_weathernext3, weathernext3, weathernext_3, google_weathernext).
- Les seaux GCS weathernext3_spatial, weathernext3_statistics_spatial et weathernext répondent ['401', '403'] sans compte Google autorisé.
- Pas de GOOGLE_APPLICATION_CREDENTIALS : BigQuery weathernext_3_0_0_0p05deg et Earth Engine sont inaccessibles ici.

Prochain fetch minimal pour débloquer :
1. Formulaire : https://developers.google.com/weathernext/guides/access-forecast
2. Attendre l'autorisation Google (ils indiquent 5 à 7 jours ouvrés).
3. Lire weathernext_3_0_0_0p05deg (ou GCS weathernext3_spatial) aux 18 stations, J0 et J-1 séparés, au moins 30 jours distincts.
4. Relancer ce script avec le compte autorisé.

## Version la plus proche disponible : WeatherNext 2 (Open-Meteo)

Modèle API : `google_weathernext2_ensemble`. Ce n'est pas WeatherNext 3 (pas de grille 0,05°, pas d'init horaire, pas de table BigQuery station).

Historical Forecast (premières heures de chaque run, donc J0 approximatif) : jours remplis ['2026-09-09', '2026-09-10', '2026-09-11', '2026-09-12']. Holdout d'août (3-6 août) : 0 cellules remplies (zéro = pas d'archive longue).

Previous Runs `previous_day1` (J-1) : cellules remplies 0. Vide = J-1 pas mesurable avec Open-Meteo.

Single Runs : les runs demandés n'ont pas été servis (voir weathernext_skill.json).

On note seulement les jours où les membres sont remplis et où le CLI existe.
J0 et J-1 ne sont pas mélangés.

### J0 : WeatherNext 2 contre le chiffre officiel (bins synthétiques)

| horizon | n bins | n dates | Brier WeatherNext 2 |
|---|---|---|---|
| J0 | 672 | 4 | 0.1400 |

### J-1 : WeatherNext 2 contre le chiffre officiel

| horizon | n bins | n dates | Brier WeatherNext 2 |
|---|---|---|---|

J-1 : aucune ligne. Previous Runs n'a renvoyé aucun membre rempli.
Pas de score J-1, pas de score inventé.

### J0 par max / min

| variable | n bins | n dates | Brier WeatherNext 2 |
|---|---|---|---|
| temp_max | 336 | 4 | 0.1417 |
| temp_min | 336 | 4 | 0.1383 |

Prix de marché J0 (kalshi_mid le jour même). Lignes écartées : {'no_wn_members': 112}.

### J0 contre le prix et le mélange actuel

| horizon | n bins | n dates | Brier WeatherNext 2 | Brier mélange (champion) | Brier marché |
|---|---|---|---|---|---|
| J0 | 200 | 3 | 0.2113 | 0.1770 | 0.0742 |

J-1 marché : aucune ligne WeatherNext 2 (membres J-1 absents). Écarts : {'no_wn_members': 248, 'no_cli_truth': 56}.

### Victoires jour par jour (WeatherNext 2 seulement)

| comparaison | jours | victoires du premier | chance que ce soit le hasard |
|---|---|---|---|
| wn2_j0_vs_market | 3 | 0 | 1.0000 |
| wn2_j0_vs_champion | 3 | 1 | 0.8750 |

Jours J0 notés (CLI) : 4 (2026-09-09, 2026-09-10, 2026-09-11, 2026-09-12).
Jours J-1 notés (CLI) : 0 (aucun).
La règle du projet demande de battre le marché sur au moins 30 jours distincts.
On ne change pas le modèle en ligne.

