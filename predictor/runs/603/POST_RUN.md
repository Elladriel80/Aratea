**Run 603 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Aug 1, 2026?
Bin cible : `KXLOWTMIA-26AUG01-B79.5` · Outcome : NO · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.257, Brier=0.0658, P&L réel=$+53.87
- `learned_v2` (challenger) — p_yes=0.111, Brier=0.0124, P&L théorique=$+53.87 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.405, Brier=0.1640, P&L théorique=$+53.87

Verdict run 603 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/603/report.json
