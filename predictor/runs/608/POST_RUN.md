**Run 608 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Aug 3, 2026?
Bin cible : `KXLOWTLAX-26AUG03-B67.5` · Outcome : YES · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.400, Brier=0.3606, P&L réel=$-82.68
- `learned_v2` (challenger) — p_yes=0.228, Brier=0.5953, P&L théorique=$-82.68
- `kalshi_mid_baseline` (baseline) — p_yes=0.610, Brier=0.1521, P&L théorique=$-82.68 ⭐

Verdict run 608 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/608/report.json
