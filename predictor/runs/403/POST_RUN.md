**Run 403 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jul 7, 2026?
Bin cible : `KXLOWTDC-26JUL07-B73.5` · Outcome : YES · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.370, Brier=0.3963, P&L réel=$+140.76
- `learned_v2` (challenger) — p_yes=0.562, Brier=0.1919, P&L théorique=$+140.76 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.310, Brier=0.4761, P&L théorique=$+140.76

Verdict run 403 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/403/report.json
