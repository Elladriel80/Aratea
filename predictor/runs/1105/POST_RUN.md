**Run 1105 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Nov 5, 2026?
Bin cible : `KXLOWTDEN-26NOV05-B35.5` · Outcome : YES · Low observée (bin gagnant) : 35-36°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.093, Brier=0.8220, P&L réel=$-128.93
- `learned_v2` (challenger) — p_yes=0.111, Brier=0.7897, P&L théorique=$-128.93
- `kalshi_mid_baseline` (baseline) — p_yes=0.325, Brier=0.4556, P&L théorique=$-128.93 ⭐

Verdict run 1105 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1105/report.json
