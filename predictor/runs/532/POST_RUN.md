**Run 532 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Jul 23, 2026?
Bin cible : `KXLOWTBOS-26JUL23-B57.5` · Outcome : NO · Low observée (bin gagnant) : ≥60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.001, Brier=0.0000, P&L réel=$+2.59 ⭐
- `learned_v2` (challenger) — p_yes=0.070, Brier=0.0049, P&L théorique=$+2.59
- `kalshi_mid_baseline` (baseline) — p_yes=0.055, Brier=0.0030, P&L théorique=$+2.59

Verdict run 532 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/532/report.json
