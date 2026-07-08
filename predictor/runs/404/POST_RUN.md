**Run 404 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on Jul 7, 2026?
Bin cible : `KXLOWTBOS-26JUL07-B62.5` · Outcome : YES · Low observée (bin gagnant) : 62-63°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.448, Brier=0.3045, P&L réel=$+15.62
- `learned_v2` (challenger) — p_yes=0.639, Brier=0.1305, P&L théorique=$+15.62 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.375, Brier=0.3906, P&L théorique=$+15.62

Verdict run 404 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/404/report.json
