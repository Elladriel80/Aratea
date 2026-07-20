**Run 499 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jul 19, 2026?
Bin cible : `KXLOWTDC-26JUL19-B76.5` · Outcome : NO · Low observée (bin gagnant) : 74-75°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.252, Brier=0.0634, P&L réel=$+43.68
- `learned_v2` (challenger) — p_yes=0.093, Brier=0.0086, P&L théorique=$+43.68 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.420, Brier=0.1764, P&L théorique=$+43.68

Verdict run 499 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/499/report.json
