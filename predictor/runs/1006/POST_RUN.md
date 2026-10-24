**Run 1006 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Oct 22, 2026?
Bin cible : `KXLOWTPHX-26OCT22-B68.5` · Outcome : NO · Low observée (bin gagnant) : ≥71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.228, Brier=0.0521, P&L réel=$+38.86 ⭐
- `learned_v2` (challenger) — p_yes=0.403, Brier=0.1625, P&L théorique=$+38.86
- `kalshi_mid_baseline` (baseline) — p_yes=0.290, Brier=0.0841, P&L théorique=$+38.86

Verdict run 1006 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1006/report.json
