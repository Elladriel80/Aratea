**Run 774 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Sep 21, 2026?
Bin cible : `KXLOWTPHX-26SEP21-B78.5` · Outcome : NO · Low observée (bin gagnant) : ≥81°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.029, Brier=0.0009, P&L réel=$+5.10 ⭐
- `learned_v2` (challenger) — p_yes=0.083, Brier=0.0069, P&L théorique=$+5.10
- `kalshi_mid_baseline` (baseline) — p_yes=0.085, Brier=0.0072, P&L théorique=$+5.10

Verdict run 774 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/774/report.json
