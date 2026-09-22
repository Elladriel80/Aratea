# Second marché : Kalshi contre Polymarket

Mesure reproductible. Aucun prix inventé. Champion inchangé.

## Données déjà dans le dépôt

- Captures `forward_*.json` : 70 fichiers, 16158 lignes.
- Contrats max Kalshi : 7770 dont 7710 avec un prix deux côtés.
- Jours Kalshi max : 70 (2026-05-08 à 2026-09-12).
- Fichiers Polymarket suivis dans git au départ : 1.
- Vérité CLI : oui (`cli_daily.json`).

## Polymarket lu sur l'API publique

- Source événements : `https://gamma-api.polymarket.com` (séries `*-daily-weather`).
- Source prix : `https://clob.polymarket.com/prices-history` (dernier point ≤ heure de capture).
- Villes « Highest temperature » ouvertes le 12 septembre 2026 : 48 (liste mesurée, pas le chiffre 44 du journal).
- Événements HIGH extraits pour les villes mappables : 2785.

## Recouvrement

- Lignes Kalshi max dans une ville mappable : 3732.
- Lignes gardées tous leads (même case, prix Polymarket avant la capture, CLI) : 1323.
- Dont la veille (lead 1) : 649 lignes, 159 villes-jours, 58 jours.
- Villes (lead 1) : ATLANTA, DALLAS, HOUSTON, MIAMI, SANFRANCISCO, SEATTLE.
- Lignes écartées : {"no_exact_bin": 2341, "no_pm_event": 60, "no_cli": 8}.

Villes Kalshi max sans série Polymarket quotidienne trouvée : BOSTON, LASVEGAS, MINNEAPOLIS, PHOENIX, SANANTONIO.

## Résultat principal (la veille, lead 1)

Plus le score d'erreur (Brier) est petit, mieux c'est.

| Méthode | Score d'erreur |
|---|---|
| Prix Kalshi | 0.1397 |
| Prix Polymarket | 0.1422 |
| Moyenne des deux | 0.1393 |
| Kalshi + écart (poids 0.0567) | 0.1395 |

Écart absolu moyen des prix : 0.0615.
Polymarket bat Kalshi : 27 jours sur 58 (p=0.7441).
La moyenne bat Kalshi : 27 jours sur 58 (p=0.7441).

## Même station NOAA (sous-ensemble)

Lignes : 520. Villes-jours : 128. Jours : 57.
Brier Kalshi 0.1437 / Polymarket 0.1433 / moyenne 0.1419.

## Autres tranches

- tous_leads : n=1323 bins, 184 villes-jours, 66 jours ; Brier K 0.1159 / PM 0.1368 / moy 0.1211 ; |écart| 0.0863.
- lead_0 : n=674 bins, 167 villes-jours, 61 jours ; Brier K 0.0930 / PM 0.1315 / moy 0.1036 ; |écart| 0.1101.
- lead_1 : n=649 bins, 159 villes-jours, 58 jours ; Brier K 0.1397 / PM 0.1422 / moy 0.1393 ; |écart| 0.0615.
- lead_1_meme_station : n=520 bins, 128 villes-jours, 57 jours ; Brier K 0.1437 / PM 0.1433 / moy 0.1419 ; |écart| 0.0610.
- lead_1_avant_3_aout : n=482 bins, 118 villes-jours, 46 jours ; Brier K 0.1456 / PM 0.1495 / moy 0.1460 ; |écart| 0.0598.
- lead_1_depuis_3_aout : n=167 bins, 41 villes-jours, 12 jours ; Brier K 0.1227 / PM 0.1213 / moy 0.1200 ; |écart| 0.0666.

Seuil habituel du projet pour parler du marché : 30 jours.
Jours (lead 1) : 58.

Verdict machine : testee_ca_n_aide_pas

