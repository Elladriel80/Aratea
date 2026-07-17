**Run 475 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jul 16, 2026?
Bin cible : `KXLOWTLAX-26JUL16-B70.5` · Outcome : NO · Low observée (bin gagnant) : 68-69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.543, Brier=0.2945, P&L réel=$-69.75
- `learned_v2` (challenger) — p_yes=0.557, Brier=0.3103, P&L théorique=$-69.75
- `kalshi_mid_baseline` (baseline) — p_yes=0.125, Brier=0.0156, P&L théorique=$-69.75 ⭐

Verdict run 475 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/475/report.json
