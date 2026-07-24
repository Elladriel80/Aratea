**Run 527 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jul 23, 2026?
Bin cible : `KXLOWTLAX-26JUL23-B67.5` · Outcome : YES · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.204, Brier=0.6342, P&L réel=$+250.75 ⭐
- `learned_v2` (challenger) — p_yes=0.048, Brier=0.9060, P&L théorique=$+250.75
- `kalshi_mid_baseline` (baseline) — p_yes=0.150, Brier=0.7225, P&L théorique=$+250.75

Verdict run 527 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/527/report.json
