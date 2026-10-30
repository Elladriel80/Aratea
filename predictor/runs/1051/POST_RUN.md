**Run 1051 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Oct 29, 2026?
Bin cible : `KXLOWTSFO-26OCT29-B54.5` · Outcome : NO · Low observée (bin gagnant) : 52-53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.358, Brier=0.1284, P&L réel=$-137.02
- `learned_v2` (challenger) — p_yes=0.175, Brier=0.0308, P&L théorique=$-137.02 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.260, Brier=0.0676, P&L théorique=$-137.02

Verdict run 1051 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1051/report.json
