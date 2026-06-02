# Décision — Fermeture de la piste climatologie « windowed » (5–8 ans)

**Date** : 2026-06-02
**Statut** : DÉCISION ACTÉE — `PIVOT_REJETÉ`
**Portée** : modèle prédictif (Phase 1 Kalshi POC). Aucune incidence on-chain.

> **EN TL;DR.** The short-window climatology track (`years_back` = 5/8 instead of 15)
> is closed. Across every series tested, no configuration produced a positive Brier
> Skill Score (BSS > 0). An 8-year window is marginally less bad than 15 years but
> never beats the constant base-rate baseline. The production `ClimatologyPredictor`
> stays as an unchanged baseline; no `ARATEA_CLIMATO_YEARS_BACK` flag is added. Phase B
> activation gate **G1 remains not met** (best series KXHIGHTSFO: N=536, BSS=−0.094).

## 1. Contexte

Le sprint « climato windowed » (2026-05-25, sessions 2 et 3) testait l'hypothèse que
réduire la fenêtre climatologique de 15 ans à 5–8 ans restaurerait un edge positif, en
pondérant davantage le réchauffement récent au lieu de le diluer dans 15 ans
d'historique. C'était la dernière variante de la **climatologie pure** restant à
écarter ou à valider avant de fermer la famille.

## 2. Preuves (du moins agrégé au plus agrégé)

### 2.1 Session 3 — 4 séries témoins (y15 / y8 / y5)

| Série | Groupe | BSS y15 | BSS y8 | Meilleur |
| --- | --- | --- | --- | --- |
| KXLOWTNYC | coastal | −0.044 | −0.076 | y5 (toujours < 0) |
| KXHIGHTSFO | coastal | −0.089 | −0.083 | y8 ✅ mais < 0 |
| KXLOWTCHI | continental | −0.105 | −0.089 | y8 ✅ mais < 0 |
| KXLOWTPHX | continental | −0.780 | −0.742 | y8 ✅ mais < 0 |

5 couples (série × config) sur 8 s'améliorent vs y15, mais **0/8 ne passe BSS > 0**.
Sweet spot apparent : `years_back = 8`.

### 2.2 Extension y8 — 16 séries

Verdict consolidé du sprint (extension aux 12 séries restantes) :
**0/16 séries avec BSS y8 > 0**, ΔBSS médian légèrement positif (y8 un peu moins négatif
que y15). La fenêtre courte réduit le biais sans jamais créer d'edge exploitable.

### 2.3 Re-mesure de la gate ce jour (2026-06-02)

Série historiquement la plus favorable (SFO HIGH), via
`scripts/_aggregate_sfo_high.py --series KXHIGHTSFO --json` :

```json
{"series": "KXHIGHTSFO", "N": 536, "base_rate": 0.1996,
 "brier_model": 0.1748, "brier_baseline_const": 0.1598,
 "bss": -0.0943, "verdict": "NO_EDGE", "edge_confirmed": false}
```

Le modèle climatologie fait **pire** que la constante au base-rate (Brier 0.175 vs
0.160). N = 536 est largement au-dessus du seuil N ≥ 200 : le verrou n'est pas le volume
de données, c'est l'absence de signal.

## 3. Décision

1. **La piste climatologie pure (toutes fenêtres, windowed inclus) est fermée.** On ne
   re-teste plus `years_back`, ni la pondération exponentielle, comme leviers principaux.
2. **`predictor/src/predictors/climatology.py` reste inchangé**, conservé comme
   *baseline de référence* (sert à mesurer le skill des prédicteurs suivants). On
   n'ajoute **pas** le flag `ARATEA_CLIMATO_YEARS_BACK` : il n'apporterait aucun edge.
3. **Aucune modification du cron live / `daily_auto.py`.**

## 4. Conséquence sur la gate Phase B (G1)

La gate d'activation Phase B (cf. `predictor/PHASE_B_SCAFFOLDING.md`, condition G1 :
`edge_confirmed=true` à BSS > 0,05 sur N ≥ 200) **reste non franchie** au 2026-06-02 :
la climatologie seule donne un BSS négatif. Aucun fichier ne se crée sous
`predictor/src/seasonal/` tant que G1 n'est pas validée par un prédicteur à edge positif.

## 5. Pistes complémentaires restant ouvertes (non engagées ici)

À explorer dans des sessions dédiées, comme leviers **au-delà** de la climatologie pure :

- tendance linéaire robuste (Theil-Sen) sur la dérive saisonnière récente ;
- features exogènes ENSO / SST / AO-NAO en entrée d'un prédicteur appris ;
- blend climatologie + forecast vendor (déjà esquissé dans `forecast_blend.py`) recalibré.

Ces pistes ne sont **pas** des engagements : elles sont listées pour mémoire.

## 6. Fichiers de travail liés (scratch, à archiver/supprimer)

Voir le débrief de session pour la liste complète et la recommandation de ménage des
scripts exploratoires `predictor/scripts/_*.py` et des briefs `_BRIEF_session_*.md`.
