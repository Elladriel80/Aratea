**Run 723 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Sep 15, 2026?
Bin cible : `KXLOWTPHX-26SEP15-B81.5` · Outcome : NO · Low observée (bin gagnant) : 83-84°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.314, Brier=0.0983, P&L réel=$-55.02
- `learned_v2` (challenger) — p_yes=0.491, Brier=0.2407, P&L théorique=$-55.02
- `kalshi_mid_baseline` (baseline) — p_yes=0.210, Brier=0.0441, P&L théorique=$-55.02 ⭐

Verdict run 723 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/723/report.json
