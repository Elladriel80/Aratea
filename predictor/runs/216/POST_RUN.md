**Run 216 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 12, 2026?
Bin cible : `KXLOWTDC-26JUN12-B71.5` · Outcome : YES · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.199, Brier=0.6421, P&L réel=$+347.82 ⭐
- `learned_v2` (challenger) — p_yes=0.097, Brier=0.8151, P&L théorique=$+347.82
- `kalshi_mid_baseline` (baseline) — p_yes=0.065, Brier=0.8742, P&L théorique=$+347.82

Verdict run 216 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/216/report.json
