**Run 388 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Jul 5, 2026?
Bin cible : `KXLOWTMIA-26JUL05-B76.5` · Outcome : YES · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.081, Brier=0.8450, P&L réel=$-16.07
- `learned_v2` (challenger) — p_yes=0.015, Brier=0.9707, P&L théorique=$-16.07
- `kalshi_mid_baseline` (baseline) — p_yes=0.235, Brier=0.5852, P&L théorique=$-16.07 ⭐

Verdict run 388 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/388/report.json
