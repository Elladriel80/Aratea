**Run 1130 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Nov 9, 2026?
Bin cible : `KXLOWTCHI-26NOV09-B41.5` · Outcome : NO · Low observée (bin gagnant) : 39-40°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.325, Brier=0.1057, P&L réel=$-109.06
- `learned_v2` (challenger) — p_yes=0.614, Brier=0.3773, P&L théorique=$-109.06
- `kalshi_mid_baseline` (baseline) — p_yes=0.095, Brier=0.0090, P&L théorique=$-109.06 ⭐

Verdict run 1130 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1130/report.json
