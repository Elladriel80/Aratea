**Run 900 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 7, 2026?
Bin cible : `KXHIGHTSFO-26OCT07-B81.5` · Outcome : NO · Low observée (bin gagnant) : ≤77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.189, Brier=0.0356, P&L réel=$-57.83
- `learned_v2` (challenger) — p_yes=0.349, Brier=0.1216, P&L théorique=$-57.83
- `kalshi_mid_baseline` (baseline) — p_yes=0.075, Brier=0.0056, P&L théorique=$-57.83 ⭐

Verdict run 900 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/900/report.json
