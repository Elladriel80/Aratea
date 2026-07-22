**Run 515 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 21, 2026?
Bin cible : `KXLOWTCHI-26JUL21-B68.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.556, Brier=0.3089, P&L réel=$-54.74
- `learned_v2` (challenger) — p_yes=0.907, Brier=0.8232, P&L théorique=$-54.74
- `kalshi_mid_baseline` (baseline) — p_yes=0.230, Brier=0.0529, P&L théorique=$-54.74 ⭐

Verdict run 515 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/515/report.json
