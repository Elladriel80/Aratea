**Run 722 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Phoenix on Sep 15, 2026?
Bin cible : `KXLOWTPHX-26SEP15-B83.5` · Outcome : YES · Low observée (bin gagnant) : 83-84°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.209, Brier=0.6260, P&L réel=$-54.68
- `learned_v2` (challenger) — p_yes=0.324, Brier=0.4572, P&L théorique=$-54.68
- `kalshi_mid_baseline` (baseline) — p_yes=0.325, Brier=0.4556, P&L théorique=$-54.68 ⭐

Verdict run 722 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/722/report.json
