**Run 1183 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Nov 16, 2026?
Bin cible : `KXHIGHTSFO-26NOV16-B58.5` · Outcome : YES · Low observée (bin gagnant) : 58-59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.232, Brier=0.5893, P&L réel=$+797.71
- `learned_v2` (challenger) — p_yes=0.264, Brier=0.5414, P&L théorique=$+797.71 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.145, Brier=0.7310, P&L théorique=$+797.71

Verdict run 1183 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1183/report.json
