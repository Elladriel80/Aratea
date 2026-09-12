**Run 691 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Sep 11, 2026?
Bin cible : `KXLOWTSEA-26SEP11-B54.5` · Outcome : NO · Low observée (bin gagnant) : 52-53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.448, Brier=0.2010, P&L réel=$+94.87 ⭐
- `learned_v2` (challenger) — p_yes=0.518, Brier=0.2681, P&L théorique=$+94.87
- `kalshi_mid_baseline` (baseline) — p_yes=0.530, Brier=0.2809, P&L théorique=$+94.87

Verdict run 691 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/691/report.json
