# Phase B — Seasonal predictor scaffolding (no implementation)

> **Statut** : scaffolding uniquement — aucune implémentation ne démarre avant la gate Phase 1 (BSS > 0,05 sur N ≥ 200 cf. `scripts/_aggregate_sfo_high.py --json --n-gate 200 --bss-gate 0.05`).
>
> **Cible** : 4 produits paramétriques Tier 1 + 6 Tier 2, horizon 3–12 mois. Le Kalshi POC 2-week reste la marche de validation méthodologique ; Phase B est le vrai produit Aratea.
>
> **Date** : 2026-05-28. Verrouillé selon `project_seasonal_phase_b` (memory 2026-05-15).

---

## 1. Gate d'activation Phase B

Une cible Phase B n'entre en implémentation que si TOUTES les conditions suivantes sont remplies, vérifiables on-chain ou via le repo :

| # | Condition | Mesure | Statut courant |
| --- | --- | --- | --- |
| G1 | Edge Phase 1 (Kalshi) prouvé | `_aggregate_sfo_high.py --json` ⇒ `edge_confirmed=true` | À reconfirmer N≥200 |
| G2 | Bankroll bootstrap atteinte | NAV pool ≥ seuil paramétré, vote DAO | Phase 1 paper-only — non applicable |
| G3 | Source de données saisonnière qualifiée | Backtest leave-one-season-out sur ≥ 10 saisons historiques | Pas encore lancé |
| G4 | Oracle disponible pour le trigger | Module `IWeatherSource` opérationnel sur la source | Reclaim POC v2 live, à étendre |
| G5 | Statuts/légal validés cabinet | Cf. mémo `memo-juridique-trigger-driven-2026-05-28.md` §6.1 | TODO-HUMAIN |

**Tant que G1 n'est pas validée, ce document reste un scaffolding — aucun fichier Python ne se crée sous `predictor/src/seasonal/`.**

---

## 2. Architecture cible — modules à créer (post-gate)

Arbre prévu pour `predictor/src/seasonal/` :

```
predictor/src/seasonal/
├── __init__.py
├── targets/                    # une cible = un fichier
│   ├── drought_med.py          # Tier 1
│   ├── drought_us.py           # Tier 1
│   ├── drought_india.py        # Tier 1
│   ├── hurricane_triggers.py   # Tier 1 (3 sous-triggers)
│   ├── hail_summer_fr.py       # Tier 2
│   ├── frost_orchard_fr.py     # Tier 2
│   ├── flood_southeast_asia.py # Tier 2
│   ├── heatwave_paris.py       # Tier 2
│   ├── el_nino_strength.py     # Tier 2
│   └── monsoon_west_africa.py  # Tier 2
├── horizons.py                 # 3/6/9/12 mois — discrétisation
├── feature_pipeline.py         # SST, AO/NAO, ENSO indices, soil moisture
├── backtest_seasonal.py        # leave-one-season-out
└── validation_gate.py          # vérifie G1-G5 avant d'autoriser un mint
```

Le pattern reproduit `predictor/src/predictors/` (climatology + forecast_blend + learned + ensemble) — ne PAS dupliquer le code, importer le `base.py`.

---

## 3. Tier 1 — spécifications des 4 cibles

### 3.1 Drought Med — sécheresse Méditerranée occidentale

**Underlying.** Standardized Precipitation Index (SPI-6) sur les bassins méditerranéens occidentaux (Espagne, sud de la France, Italie nord-ouest, Maghreb), agrégé sur 6 mois glissants.

**Trigger.** SPI-6 ≤ −1,5 (sécheresse sévère) en moyenne pondérée par superficie agricole sur la zone, mesuré à T+6 mois après émission.

**Sources oracle.**
- **Primaire** : Copernicus C3S Climate Data Store (ECMWF SEAS5 saisonnier + ERA5 reanalysis), via Reclaim Protocol.
- **Secondaire** : NCEP CFSv2 (NOAA), pour cross-check.
- **Tertiaire (Phase 4)** : DePIN soil moisture stations méditerranéennes.

**Features pressenties.**
| Feature | Hypothèse | Source |
| --- | --- | --- |
| `sst_north_atlantic_3mo` | Une anomalie SST +0,5°C en Atlantique nord pré-décale les fronts | NOAA ERSSTv5 |
| `nao_winter_index` | NAO+ pousse les dépressions au nord, assèche le sud | NOAA CPC |
| `enso_3.4_lagged_6m` | El Niño fort augmente la prob. de sécheresse Med suivante | NOAA ONI |
| `previous_season_spi` | Autocorrélation SPI > 6 mois | Copernicus |
| `soil_moisture_anom_t0` | État initial du sol conditionne la traçabilité | ESA CCI |

**Volumes attendus.**
- Strike réaliste : 5–15 % de probabilité historique (queue lourde).
- Tailles contrat : 100–10 000 USD payout.
- N à viser pour validation : 30 saisons (ERA5 1991–2020 + 2021–2026 OOS).

**Risques métier.** Basis risk élevé pour un agriculteur individuel — la zone est large. À considérer : décliner en sous-zones (Estrémadure, Catalogne, Provence, Sicile, etc.) avec un sous-pool dédié.

### 3.2 Drought US — sécheresse US Heartland

**Underlying.** US Drought Monitor (USDM) D2+ (drought severe ou pire) sur la zone Heartland (Iowa, Kansas, Nebraska, Missouri, Illinois), mesuré au pic de saison (août).

**Trigger.** ≥ 30 % de la superficie Heartland classée USDM D2+ à T+5 mois.

**Sources oracle.**
- **Primaire** : USDA + NDMC US Drought Monitor weekly, via Reclaim.
- **Secondaire** : NOAA CPC seasonal drought outlook.

**Features pressenties.**
| Feature | Hypothèse | Source |
| --- | --- | --- |
| `enso_3.4_dec_jan` | La NeƱa hivernale → printemps sec Midwest | NOAA ONI |
| `pdo_phase` | Phase PDO+ couplée à NeƱa accroît le risque | NOAA ESRL |
| `snowpack_rockies_apr` | Faible snowpack rocheuses = faible apport rivières | NRCS SNOTEL |
| `soil_moisture_may_iowa` | État initial juin conditionne pic août | NOAA CPC |
| `evapotranspiration_anom_jjm` | Anomalie ET juin-juillet anticipe pic D2 | MODIS / Sentinel-3 |

**Volumes attendus.**
- Strike : 10–20 % prob. historique (2012, 2022, 2023 = années D2+).
- Tailles : 1 000–100 000 USD (agribusiness, traders céréaliers).
- N validation : 26 saisons (USDM commence 2000).

**Risque métier.** Faible N historique (26 ans) → backtest power limité, nécessité de bootstrap + intervalle de confiance large.

### 3.3 Drought India — mousson SW

**Underlying.** Indian Monsoon Rainfall (IMD All-India Summer Monsoon Rainfall, juin–septembre), benchmark vs Long Period Average (LPA).

**Trigger.** Saison classée *deficient* par IMD (< 90 % LPA national, ou < 75 % LPA dans ≥ 4 sous-divisions homogènes).

**Sources oracle.**
- **Primaire** : IMD (India Meteorological Department) bulletins via Reclaim, données disponibles fin octobre N.
- **Secondaire** : ECMWF SEAS5 pré-saison (mai), pour pricing.

**Features pressenties.**
| Feature | Hypothèse | Source |
| --- | --- | --- |
| `enso_3.4_apr_may` | El Niño pré-mousson supprime statistiquement la mousson | NOAA ONI |
| `iod_strength_may_jun` | Indian Ocean Dipole+ contrebalance El Niño | BOM/IOD |
| `snow_eurasian_winter` | Anomalie snow cover Eurasie → variabilité mousson | Rutgers GSL |
| `qbo_phase` | Quasi-Biennial Oscillation 30hPa affecte propagation MJO | NOAA NCEI |
| `previous_mousson_anomaly` | Auto-corr. faible mais non-nulle | IMD historique |

**Volumes attendus.**
- Strike : 15–25 % prob. historique.
- Cible buyers : exportateurs agriculteurs Indes / fonds macro / réassureurs hedging crop. Pricing en USD pool, payout en INR si jurisdiction permet.
- N validation : 150 saisons IMD (1871–) — excellent power.

**Risque métier.** Sensibilité politique sur publication officielle indienne. Backup Copernicus C3S obligatoire.

### 3.4 Hurricane triggers — 3 sous-triggers atlantique nord

Cible composite Tier 1 — 3 sous-contrats sur la saison ouragans Atlantique nord (NHC, juin–novembre).

**3.4a. Trigger ACE — Accumulated Cyclone Energy.**
- Trigger : ACE saisonnier total ≥ 159 (seuil saison « hyperactive » NHC).
- Source : NHC + Colorado State University Tropical Met seasonal recap (publié décembre N).
- Strike historique : ~20 % saisons.

**3.4b. Trigger Major Hurricane US Landfall.**
- Trigger : ≥ 1 ouragan Catégorie 3+ touchant terre US continental durant la saison.
- Source : NHC TC reports + USGS landfall records.
- Strike historique : ~50 % saisons (très liquide).

**3.4c. Trigger Named Storms ≥ 18.**
- Trigger : nombre de named storms ≥ 18 (vs moyenne climatologique 14,4 sur 1991–2020).
- Source : NHC.
- Strike historique : ~30 % saisons depuis 2005.

**Features communes aux 3 sous-triggers.**
| Feature | Hypothèse | Source |
| --- | --- | --- |
| `mdr_sst_anom_apr_may` | Main Development Region SST avant juin = #1 prédicteur | NOAA ERSSTv5 |
| `enso_jas` | Cisaillement Atlantique modulé par ENSO été | NOAA ONI |
| `sahel_rainfall_jjm` | Mousson Sahel + → vagues d'est plus actives | CHIRPS |
| `west_african_easterly_jet` | Position WAEJ influence cyclogenèse | ECMWF ERA5 |
| `csu_forecast_may` | Forecast CSU mai est une bonne baseline | CSU TMP |

**Volumes attendus.**
- Strike A : 20 %, B : 50 %, C : 30 % — couvre le spectre.
- Tailles : 1 000–500 000 USD (réinsurers, traders énergie/fret, propriétaires côtiers).
- N validation : 50+ saisons NHC HURDAT2.

**Risque métier.** Corrélation entre les 3 sous-triggers — pool doit gérer la corrélation (covar matrix dans `validation_gate.py`).

---

## 4. Tier 2 — résumé (à expanser post-Tier 1)

| Cible | Trigger | Source primaire | Strike approx. | Priorité d'implémentation |
| --- | --- | --- | --- | --- |
| Hail summer FR | Surface grêle ≥ X km² | KraussNet / OdyseE | 30 % | T2.1 |
| Frost orchard FR | T_min ≤ −2 °C en avril sur vergers ref | Météo-France | 25 % | T2.2 |
| Flood SE Asia | Inondation Mekong/Bangkok au-dessus seuil | Copernicus EMS | 15 % | T2.3 |
| Heatwave Paris | ≥ 5 jours T_max ≥ 35 °C juillet-août | Météo-France | 35 % | T2.4 |
| ENSO strength | NeƱa/Niño fort à Nov-Dec N | NOAA ONI | 30 % | T2.5 |
| Monsoon West Africa | Sahel rainfall jjm < X mm | CHIRPS | 20 % | T2.6 |

---

## 5. Backtest leave-one-season-out — protocole

Le seul protocole admissible pour valider une cible Tier 1 :

1. **Train** : toutes les saisons sauf 1.
2. **Predict** : la saison out, à partir des features connues à T-mois (forecast horizon).
3. **Score** : Brier sur le binaire trigger/no-trigger.
4. **Repeat** sur toutes les saisons disponibles.
5. **Baselines** :
   - climatology (base rate historique de la saison),
   - seasonal forecast vendor brut (ECMWF SEAS5),
   - mid-market d'un éventuel marché paramétrique préexistant (Speedwell, OS).
6. **Gate publication** : BSS > 0,05 vs *toutes* les baselines simultanément. Si le modèle bat climatology mais perd contre SEAS5, **on n'écrit pas de contrats** — on documente l'écart et on cherche features supplémentaires (cf. discipline §3.3 du whitepaper, FEATURES.md).

---

## 6. Vocabulaire publique (rappel mémoire)

Conformément à `feedback_no_assurance_terminology` :
- ✅ « couverture paramétrique », « mutuelle décentralisée », « trigger »
- ❌ « assurance », « indemnisation », « assuré », « assureur »

Conformément à `feedback_token_not_for_trading` :
- ✅ « part de NAV », « droit de gouvernance »
- ❌ « cours du token », « cap pour protéger le prix », « rendement »

---

## 7. Ce qui reste à décider — fork-in-road

- **§7.1** — *Décliner Drought Med en sous-zones* ? oui = plus de granularité, non = plus de liquidité pool unique. Décision : à la sortie de gate G1, en fonction du volume d'intérêt cabling-up Discord.
- **§7.2** — *Couverture jurisdictionnelle des Tier 1* : on offre Drought India à des buyers résidant Inde ? cf. mémo juridique §6.2.
- **§7.3** — *Pool unique vs sous-pools par tier* : la spec actuelle prévoit pool unique (cf. `project_financial_model_v04`) ; à revoir si la corrélation hurricane fait sauter MCR.
- **§7.4** — *Pricing model* : pure Brier-derived ou ajout loading pool capacity ? Décision Phase 3.

---

*Fin du scaffolding. Implémentation conditionnée à `_aggregate_sfo_high.py --json` retournant `edge_confirmed=true`.*
