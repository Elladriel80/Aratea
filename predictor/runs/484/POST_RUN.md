**Run 484 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jul 17, 2026?
Bin cible : `KXLOWTDC-26JUL17-B74.5` · Outcome : NO · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.273, Brier=0.0747, P&L réel=$-39.68
- `learned_v2` (challenger) — p_yes=0.083, Brier=0.0069, P&L théorique=$-39.68 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.160, Brier=0.0256, P&L théorique=$-39.68

Verdict run 484 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/484/report.json
