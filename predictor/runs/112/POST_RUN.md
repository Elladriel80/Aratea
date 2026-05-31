**Run 112 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on May 30, 2026?
Bin cible : `KXLOWTPHX-26MAY30-B67.5` · Outcome : NO · Low observée (bin gagnant) : ≥68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.137, Brier=0.0187, P&L réel=$+15.23 ⭐
- `learned_v2` (challenger) — p_yes=0.500, Brier=0.2500, P&L théorique=$+15.23
- `kalshi_mid_baseline` (baseline) — p_yes=0.435, Brier=0.1892, P&L théorique=$+15.23

Verdict run 112 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/112/report.json
