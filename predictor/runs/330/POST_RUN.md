**Run 330 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Jun 26, 2026?
Bin cible : `KXLOWTPHX-26JUN26-B87.5` · Outcome : NO · Low observée (bin gagnant) : ≥88°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.259, Brier=0.0671, P&L réel=$+27.84 ⭐
- `learned_v2` (challenger) — p_yes=0.388, Brier=0.1506, P&L théorique=$+27.84
- `kalshi_mid_baseline` (baseline) — p_yes=0.320, Brier=0.1024, P&L théorique=$+27.84

Verdict run 330 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/330/report.json
