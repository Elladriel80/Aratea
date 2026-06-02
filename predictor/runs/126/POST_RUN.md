**Run 126 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Jun 1, 2026?
Bin cible : `KXLOWTCHI-26JUN01-B57.5` · Outcome : NO · Low observée (bin gagnant) : 55-56°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.149, Brier=0.0221, P&L réel=$+12.54
- `learned_v2` (challenger) — p_yes=0.071, Brier=0.0050, P&L théorique=$+12.54 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.380, Brier=0.1444, P&L théorique=$+12.54

Verdict run 126 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/126/report.json
