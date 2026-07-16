**Run 461 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 15, 2026?
Bin cible : `KXLOWTNYC-26JUL15-B79.5` · Outcome : NO · Low observée (bin gagnant) : 75-76°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.653, Brier=0.4261, P&L réel=$-68.53
- `learned_v2` (challenger) — p_yes=0.771, Brier=0.5939, P&L théorique=$-68.53
- `kalshi_mid_baseline` (baseline) — p_yes=0.445, Brier=0.1980, P&L théorique=$-68.53 ⭐

Verdict run 461 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/461/report.json
