**Run 570 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Jul 28, 2026?
Bin cible : `KXLOWTPHX-26JUL28-B87.5` · Outcome : NO · Low observée (bin gagnant) : ≤85°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.111, Brier=0.0123, P&L réel=$-78.19
- `learned_v2` (challenger) — p_yes=0.117, Brier=0.0138, P&L théorique=$-78.19
- `kalshi_mid_baseline` (baseline) — p_yes=0.035, Brier=0.0012, P&L théorique=$-78.19 ⭐

Verdict run 570 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/570/report.json
