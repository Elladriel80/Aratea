**Run 323 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 26, 2026?
Bin cible : `KXLOWTDC-26JUN26-B71.5` · Outcome : NO · Low observée (bin gagnant) : ≥72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.525, Brier=0.2753, P&L réel=$-59.32
- `learned_v2` (challenger) — p_yes=0.483, Brier=0.2337, P&L théorique=$-59.32
- `kalshi_mid_baseline` (baseline) — p_yes=0.175, Brier=0.0306, P&L théorique=$-59.32 ⭐

Verdict run 323 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/323/report.json
