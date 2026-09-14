**Run 708 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Sep 13, 2026?
Bin cible : `KXLOWTPHX-26SEP13-B82.5` · Outcome : NO · Low observée (bin gagnant) : 86-87°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.183, Brier=0.0334, P&L réel=$-53.56
- `learned_v2` (challenger) — p_yes=0.230, Brier=0.0528, P&L théorique=$-53.56
- `kalshi_mid_baseline` (baseline) — p_yes=0.130, Brier=0.0169, P&L théorique=$-53.56 ⭐

Verdict run 708 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/708/report.json
