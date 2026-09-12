**Run 688 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Sep 11, 2026?
Bin cible : `KXLOWTDC-26SEP11-B70.5` · Outcome : YES · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.071, Brier=0.8624, P&L réel=$-83.81
- `learned_v2` (challenger) — p_yes=0.021, Brier=0.9589, P&L théorique=$-83.81
- `kalshi_mid_baseline` (baseline) — p_yes=0.245, Brier=0.5700, P&L théorique=$-83.81 ⭐

Verdict run 688 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/688/report.json
