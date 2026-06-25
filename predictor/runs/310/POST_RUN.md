**Run 310 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Jun 24, 2026?
Bin cible : `KXLOWTBOS-26JUN24-B60.5` · Outcome : NO · Low observée (bin gagnant) : ≥61°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.087, Brier=0.0075, P&L réel=$+6.98 ⭐
- `learned_v2` (challenger) — p_yes=0.091, Brier=0.0083, P&L théorique=$+6.98
- `kalshi_mid_baseline` (baseline) — p_yes=0.155, Brier=0.0240, P&L théorique=$+6.98

Verdict run 310 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/310/report.json
