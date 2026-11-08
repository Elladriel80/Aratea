**Run 1118 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on Nov 7, 2026?
Bin cible : `KXLOWTBOS-26NOV07-B49.5` · Outcome : YES · Low observée (bin gagnant) : 49-50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.235, Brier=0.5852, P&L réel=$-125.36
- `learned_v2` (challenger) — p_yes=0.426, Brier=0.3299, P&L théorique=$-125.36 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.315, Brier=0.4692, P&L théorique=$-125.36

Verdict run 1118 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1118/report.json
