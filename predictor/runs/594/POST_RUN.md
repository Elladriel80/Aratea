**Run 594 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Aug 1, 2026?
Bin cible : `KXLOWTSFO-26AUG01-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.347, Brier=0.4269, P&L réel=$-78.98
- `learned_v2` (challenger) — p_yes=0.144, Brier=0.7321, P&L théorique=$-78.98
- `kalshi_mid_baseline` (baseline) — p_yes=0.595, Brier=0.1640, P&L théorique=$-78.98 ⭐

Verdict run 594 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/594/report.json
