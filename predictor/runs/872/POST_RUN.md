**Run 872 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Oct 4, 2026?
Bin cible : `KXLOWTNYC-26OCT04-B54.5` · Outcome : NO · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.256, Brier=0.0654, P&L réel=$-4.95
- `learned_v2` (challenger) — p_yes=0.378, Brier=0.1426, P&L théorique=$-4.95
- `kalshi_mid_baseline` (baseline) — p_yes=0.050, Brier=0.0025, P&L théorique=$-4.95 ⭐

Verdict run 872 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/872/report.json
