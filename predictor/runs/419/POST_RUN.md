**Run 419 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jul 9, 2026?
Bin cible : `KXLOWTDC-26JUL09-B72.5` · Outcome : NO · Low observée (bin gagnant) : ≥73°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.322, Brier=0.1037, P&L réel=$-72.65
- `learned_v2` (challenger) — p_yes=0.416, Brier=0.1734, P&L théorique=$-72.65
- `kalshi_mid_baseline` (baseline) — p_yes=0.145, Brier=0.0210, P&L théorique=$-72.65 ⭐

Verdict run 419 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/419/report.json
