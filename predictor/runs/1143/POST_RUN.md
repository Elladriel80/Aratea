**Run 1143 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Nov 11, 2026?
Bin cible : `KXLOWTNYC-26NOV11-B46.5` · Outcome : NO · Low observée (bin gagnant) : 50-51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.279, Brier=0.0776, P&L réel=$-103.68
- `learned_v2` (challenger) — p_yes=0.533, Brier=0.2842, P&L théorique=$-103.68
- `kalshi_mid_baseline` (baseline) — p_yes=0.090, Brier=0.0081, P&L théorique=$-103.68 ⭐

Verdict run 1143 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1143/report.json
