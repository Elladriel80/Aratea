**Run 622 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Aug 5, 2026?
Bin cible : `KXLOWTLAX-26AUG05-B67.5` · Outcome : YES · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.449, Brier=0.3038, P&L réel=$-72.21
- `learned_v2` (challenger) — p_yes=0.780, Brier=0.0484, P&L théorique=$-72.21 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.565, Brier=0.1892, P&L théorique=$-72.21

Verdict run 622 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/622/report.json
