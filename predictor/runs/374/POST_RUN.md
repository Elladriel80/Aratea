**Run 374 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Phoenix on Jul 3, 2026?
Bin cible : `KXLOWTPHX-26JUL03-B77.5` · Outcome : YES · Low observée (bin gagnant) : 77-78°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.138, Brier=0.7435, P&L réel=$-88.32
- `learned_v2` (challenger) — p_yes=0.214, Brier=0.6181, P&L théorique=$-88.32
- `kalshi_mid_baseline` (baseline) — p_yes=0.360, Brier=0.4096, P&L théorique=$-88.32 ⭐

Verdict run 374 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/374/report.json
