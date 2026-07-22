**Run 518 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Jul 21, 2026?
Bin cible : `KXLOWTBOS-26JUL21-B60.5` · Outcome : NO · Low observée (bin gagnant) : ≥61°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.027, Brier=0.0007, P&L réel=$+2.56 ⭐
- `learned_v2` (challenger) — p_yes=0.067, Brier=0.0044, P&L théorique=$+2.56
- `kalshi_mid_baseline` (baseline) — p_yes=0.080, Brier=0.0064, P&L théorique=$+2.56

Verdict run 518 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/518/report.json
