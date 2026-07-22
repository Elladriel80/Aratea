**Run 517 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Jul 21, 2026?
Bin cible : `KXLOWTBOS-26JUL21-B58.5` · Outcome : NO · Low observée (bin gagnant) : ≥61°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.005, Brier=0.0000, P&L réel=$+4.13 ⭐
- `learned_v2` (challenger) — p_yes=0.067, Brier=0.0045, P&L théorique=$+4.13
- `kalshi_mid_baseline` (baseline) — p_yes=0.070, Brier=0.0049, P&L théorique=$+4.13

Verdict run 517 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/517/report.json
