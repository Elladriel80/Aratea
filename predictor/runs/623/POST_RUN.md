**Run 623 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Aug 5, 2026?
Bin cible : `KXLOWTSFO-26AUG05-B58.5` · Outcome : YES · Low observée (bin gagnant) : 58-59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.507, Brier=0.2428, P&L réel=$-72.00
- `learned_v2` (challenger) — p_yes=0.701, Brier=0.0895, P&L théorique=$-72.00 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.625, Brier=0.1406, P&L théorique=$-72.00

Verdict run 623 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/623/report.json
