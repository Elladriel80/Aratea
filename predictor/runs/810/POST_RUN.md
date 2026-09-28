**Run 810 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Sep 27, 2026?
Bin cible : `KXLOWTLAX-26SEP27-B68.5` · Outcome : NO · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.570, Brier=0.3245, P&L réel=$-55.33
- `learned_v2` (challenger) — p_yes=0.915, Brier=0.8378, P&L théorique=$-55.33
- `kalshi_mid_baseline` (baseline) — p_yes=0.465, Brier=0.2162, P&L théorique=$-55.33 ⭐

Verdict run 810 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/810/report.json
