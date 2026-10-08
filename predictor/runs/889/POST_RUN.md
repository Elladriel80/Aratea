**Run 889 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Oct 7, 2026?
Bin cible : `KXLOWTLAX-26OCT07-B70.5` · Outcome : YES · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.090, Brier=0.8273, P&L réel=$-57.60
- `learned_v2` (challenger) — p_yes=0.020, Brier=0.9606, P&L théorique=$-57.60
- `kalshi_mid_baseline` (baseline) — p_yes=0.520, Brier=0.2304, P&L théorique=$-57.60 ⭐

Verdict run 889 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/889/report.json
