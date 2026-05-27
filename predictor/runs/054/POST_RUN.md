**Run 054 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on May 26, 2026?
Bin cible : `KXLOWTNYC-26MAY26-B58.5` · Outcome : YES · Low observée (bin gagnant) : 58-59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.134, Brier=0.7501, P&L réel=$-20.59
- `learned_v2` (challenger) — p_yes=0.177, Brier=0.6769, P&L théorique=$-20.59
- `kalshi_mid_baseline` (baseline) — p_yes=0.290, Brier=0.5041, P&L théorique=$-20.59 ⭐

Verdict run 054 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/054/report.json
