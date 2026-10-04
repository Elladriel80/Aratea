**Run 867 — résolu YES · Multi-model A/B**

Event : Highest temperature in Boston on Oct 3, 2026?
Bin cible : `KXHIGHTBOS-26OCT03-B67.5` · Outcome : YES · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.278, Brier=0.5209, P&L réel=$-59.80
- `learned_v2` (challenger) — p_yes=0.456, Brier=0.2955, P&L théorique=$-59.80 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.425, Brier=0.3306, P&L théorique=$-59.80

Verdict run 867 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/867/report.json
