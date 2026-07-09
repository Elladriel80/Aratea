**Run 408 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 8, 2026?
Bin cible : `KXLOWTCHI-26JUL08-B67.5` · Outcome : YES · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.348, Brier=0.4252, P&L réel=$+194.53
- `learned_v2` (challenger) — p_yes=0.575, Brier=0.1804, P&L théorique=$+194.53 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.225, Brier=0.6006, P&L théorique=$+194.53

Verdict run 408 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/408/report.json
