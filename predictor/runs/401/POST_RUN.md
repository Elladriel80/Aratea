**Run 401 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 7, 2026?
Bin cible : `KXLOWTCHI-26JUL07-B65.5` · Outcome : YES · Low observée (bin gagnant) : 65-66°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.493, Brier=0.2570, P&L réel=$+107.73
- `learned_v2` (challenger) — p_yes=0.810, Brier=0.0362, P&L théorique=$+107.73 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.370, Brier=0.3969, P&L théorique=$+107.73

Verdict run 401 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/401/report.json
