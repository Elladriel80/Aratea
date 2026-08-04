**Run 610 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Aug 3, 2026?
Bin cible : `KXLOWTSFO-26AUG03-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.554, Brier=0.1986, P&L réel=$-82.83
- `learned_v2` (challenger) — p_yes=0.510, Brier=0.2399, P&L théorique=$-82.83
- `kalshi_mid_baseline` (baseline) — p_yes=0.670, Brier=0.1089, P&L théorique=$-82.83 ⭐

Verdict run 610 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/610/report.json
