**Run 1180 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Nov 16, 2026?
Bin cible : `KXLOWTDEN-26NOV16-B32.5` · Outcome : YES · Low observée (bin gagnant) : 32-33°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.261, Brier=0.5467, P&L réel=$-135.30
- `learned_v2` (challenger) — p_yes=0.533, Brier=0.2184, P&L théorique=$-135.30 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.340, Brier=0.4356, P&L théorique=$-135.30

Verdict run 1180 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1180/report.json
