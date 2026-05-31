**Run 107 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on May 30, 2026?
Bin cible : `KXLOWTBOS-26MAY30-B45.5` · Outcome : YES · Low observée (bin gagnant) : 45-46°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.159, Brier=0.7071, P&L réel=$-19.88
- `learned_v2` (challenger) — p_yes=0.064, Brier=0.8757, P&L théorique=$-19.88
- `kalshi_mid_baseline` (baseline) — p_yes=0.290, Brier=0.5041, P&L théorique=$-19.88 ⭐

Verdict run 107 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/107/report.json
