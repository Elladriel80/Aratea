**Run 1175 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Nov 16, 2026?
Bin cible : `KXLOWTLAX-26NOV16-B58.5` · Outcome : NO · Low observée (bin gagnant) : ≥59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.545, Brier=0.2969, P&L réel=$-135.32
- `learned_v2` (challenger) — p_yes=0.900, Brier=0.8102, P&L théorique=$-135.32
- `kalshi_mid_baseline` (baseline) — p_yes=0.340, Brier=0.1156, P&L théorique=$-135.32 ⭐

Verdict run 1175 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1175/report.json
