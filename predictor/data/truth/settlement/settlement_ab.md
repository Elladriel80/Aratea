# Fenêtre d'hiver et Degré entier (comptes machine)

Date du run : 2026-09-12T16:18:26Z
Champion en ligne : non modifié. Aucun chiffre inventé.

## Fenêtre d'hiver (ASOS horaire, LST vs heure murale)

Source : IEM ASOS/METAR horaire déjà dans data/asos/extracted.json
Jours comparables : 2314
Stations : 18
Première / dernière : 2026-05-01 / 2026-09-11

| Ensemble | Jours | Max différent | Min différent | Entier max | Entier min | Case 2° |
|---|---|---|---|---|---|---|
| Tous | 2314 | 18 | 185 | 18 | 185 | 129 |
| Jours avec heure d'été | 2188 | 18 | 185 | 18 | 185 | 129 |
| Jours sans heure d'été | 126 | 0 | 0 | 0 | 0 | 0 |

### Par station

| Ville | Jours | Max différent | Min différent | Case 2° |
|---|---|---|---|---|
| Chicago | 130 | 4 | 19 | 13 |
| Philadelphie | 130 | 1 | 16 | 10 |
| Washington | 130 | 2 | 16 | 12 |
| New York | 130 | 4 | 12 | 10 |
| Seattle | 126 | 0 | 15 | 10 |
| Boston | 129 | 1 | 14 | 10 |
| Los Angeles | 126 | 0 | 12 | 6 |
| Minneapolis | 130 | 2 | 11 | 9 |
| Denver | 126 | 0 | 11 | 9 |
| San Francisco | 126 | 0 | 11 | 5 |
| Atlanta | 130 | 0 | 10 | 8 |
| Austin | 129 | 0 | 10 | 9 |
| Miami | 130 | 0 | 8 | 4 |
| Dallas | 130 | 1 | 6 | 5 |
| Houston | 130 | 3 | 3 | 4 |
| Las Vegas | 126 | 0 | 6 | 3 |
| San Antonio | 130 | 0 | 5 | 2 |
| Phoenix | 126 | 0 | 0 | 0 |

## Heures imprimées du CLI (complément, pas un changement de valeur)

Jours CLI : 44005
Max à 00:xx en heure d'été : 366 sur 43480 heures lisibles
Min à 00:xx en heure d'été : 431 sur 43498 heures lisibles
Heures max illisibles : 525 ; min illisibles : 507

## Degré entier

### METAR horaire déjà dans le dépôt

Lectures : 56302
Lectures non entières : 44
Jours LST avec assez de lectures : 2314
Jours dont le max ou le min horaire n'est pas entier : 3

### GHCN-Daily (dixième de °C → °F continu)

Les TMAX/TMIN USW sont souvent stockés depuis un °F entier. La partie fractionnaire après conversion peut être un artefact d'unité, pas un vrai demi-degré capteur.
Jours × variables : 1059816
Déjà un entier °F : 116797
Exactement x.5 : 0
Entier NWS ≠ partie entière : 465194
Entier NWS ≠ arrondi Python : 0
Case 2° différente (entier vs partie entière) : 246576
Case 2° différente (entier vs demi-degré puis partie entière) : 0

Aucun pari avec de l'argent réel. Le modèle en ligne n'est pas changé.
