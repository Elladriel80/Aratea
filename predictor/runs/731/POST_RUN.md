**Run 731 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Sep 17, 2026?
Bin cible : `KXLOWTDC-26SEP17-B66.5` · Outcome : NO · Low observée (bin gagnant) : ≥69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.243, Brier=0.0591, P&L réel=$-59.76
- `learned_v2` (challenger) — p_yes=0.352, Brier=0.1241, P&L théorique=$-59.76
- `kalshi_mid_baseline` (baseline) — p_yes=0.095, Brier=0.0090, P&L théorique=$-59.76 ⭐

Verdict run 731 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/731/report.json
