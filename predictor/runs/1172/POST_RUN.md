**Run 1172 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Nov 16, 2026?
Bin cible : `KXLOWTNYC-26NOV16-B39.5` · Outcome : YES · Low observée (bin gagnant) : 39-40°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.223, Brier=0.6046, P&L réel=$-135.36
- `learned_v2` (challenger) — p_yes=0.360, Brier=0.4101, P&L théorique=$-135.36
- `kalshi_mid_baseline` (baseline) — p_yes=0.530, Brier=0.2209, P&L théorique=$-135.36 ⭐

Verdict run 1172 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1172/report.json
