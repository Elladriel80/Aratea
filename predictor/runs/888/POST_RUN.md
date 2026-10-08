**Run 888 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Oct 7, 2026?
Bin cible : `KXLOWTNYC-26OCT07-B48.5` · Outcome : YES · Low observée (bin gagnant) : 48-49°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.222, Brier=0.6057, P&L réel=$-57.38
- `learned_v2` (challenger) — p_yes=0.060, Brier=0.8828, P&L théorique=$-57.38
- `kalshi_mid_baseline` (baseline) — p_yes=0.325, Brier=0.4556, P&L théorique=$-57.38 ⭐

Verdict run 888 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/888/report.json
