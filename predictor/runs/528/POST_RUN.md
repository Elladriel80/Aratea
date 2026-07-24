**Run 528 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 23, 2026?
Bin cible : `KXLOWTSFO-26JUL23-B56.5` · Outcome : NO · Low observée (bin gagnant) : 58-59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.149, Brier=0.0223, P&L réel=$-56.09
- `learned_v2` (challenger) — p_yes=0.026, Brier=0.0007, P&L théorique=$-56.09 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.065, Brier=0.0042, P&L théorique=$-56.09

Verdict run 528 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/528/report.json
