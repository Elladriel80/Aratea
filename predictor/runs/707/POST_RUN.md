**Run 707 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Sep 13, 2026?
Bin cible : `KXLOWTPHX-26SEP13-B84.5` · Outcome : NO · Low observée (bin gagnant) : 86-87°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.314, Brier=0.0989, P&L réel=$-70.61
- `learned_v2` (challenger) — p_yes=0.505, Brier=0.2550, P&L théorique=$-70.61
- `kalshi_mid_baseline` (baseline) — p_yes=0.230, Brier=0.0529, P&L théorique=$-70.61 ⭐

Verdict run 707 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/707/report.json
