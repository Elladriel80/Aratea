**Run 295 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Jun 22, 2026?
Bin cible : `KXLOWTBOS-26JUN22-B58.5` · Outcome : NO · Low observée (bin gagnant) : ≥59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.086, Brier=0.0075, P&L réel=$+8.17 ⭐
- `learned_v2` (challenger) — p_yes=0.090, Brier=0.0081, P&L théorique=$+8.17
- `kalshi_mid_baseline` (baseline) — p_yes=0.190, Brier=0.0361, P&L théorique=$+8.17

Verdict run 295 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/295/report.json
