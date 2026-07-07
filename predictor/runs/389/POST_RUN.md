**Run 389 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 6, 2026?
Bin cible : `KXLOWTNYC-26JUL06-B67.5` · Outcome : NO · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.531, Brier=0.2823, P&L réel=$-66.96
- `learned_v2` (challenger) — p_yes=0.460, Brier=0.2119, P&L théorique=$-66.96
- `kalshi_mid_baseline` (baseline) — p_yes=0.310, Brier=0.0961, P&L théorique=$-66.96 ⭐

Verdict run 389 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/389/report.json
