**Run 765 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Sep 21, 2026?
Bin cible : `KXLOWTCHI-26SEP21-B60.5` · Outcome : NO · Low observée (bin gagnant) : 58-59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.345, Brier=0.1189, P&L réel=$+47.43
- `learned_v2` (challenger) — p_yes=0.128, Brier=0.0164, P&L théorique=$+47.43 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.465, Brier=0.2162, P&L théorique=$+47.43

Verdict run 765 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/765/report.json
