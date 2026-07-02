**Run 351 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jul 1, 2026?
Bin cible : `KXLOWTLAX-26JUL01-B59.5` · Outcome : NO · Low observée (bin gagnant) : ≥60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.064, Brier=0.0041, P&L réel=$+13.17
- `learned_v2` (challenger) — p_yes=0.050, Brier=0.0025, P&L théorique=$+13.17 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.155, Brier=0.0240, P&L théorique=$+13.17

Verdict run 351 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/351/report.json
