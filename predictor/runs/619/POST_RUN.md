**Run 619 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Phoenix on Aug 3, 2026?
Bin cible : `KXLOWTPHX-26AUG03-B92.5` · Outcome : YES · Low observée (bin gagnant) : 92-93°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.343, Brier=0.4320, P&L réel=$-82.93
- `learned_v2` (challenger) — p_yes=0.624, Brier=0.1415, P&L théorique=$-82.93 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.465, Brier=0.2862, P&L théorique=$-82.93

Verdict run 619 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/619/report.json
