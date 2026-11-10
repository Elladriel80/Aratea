**Run 1131 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Nov 9, 2026?
Bin cible : `KXLOWTDC-26NOV09-B48.5` · Outcome : YES · Low observée (bin gagnant) : 48-49°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.403, Brier=0.3570, P&L réel=$-108.81
- `learned_v2` (challenger) — p_yes=0.802, Brier=0.0394, P&L théorique=$-108.81 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.535, Brier=0.2162, P&L théorique=$-108.81

Verdict run 1131 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1131/report.json
