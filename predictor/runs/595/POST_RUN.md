**Run 595 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Aug 1, 2026?
Bin cible : `KXLOWTSFO-26AUG01-B58.5` · Outcome : NO · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.401, Brier=0.1608, P&L réel=$-79.06
- `learned_v2` (challenger) — p_yes=0.237, Brier=0.0562, P&L théorique=$-79.06 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.295, Brier=0.0870, P&L théorique=$-79.06

Verdict run 595 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/595/report.json
