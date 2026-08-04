**Run 615 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Aug 3, 2026?
Bin cible : `KXLOWTMIA-26AUG03-B81.5` · Outcome : NO · Low observée (bin gagnant) : ≤75°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.314, Brier=0.0984, P&L réel=$-82.94
- `learned_v2` (challenger) — p_yes=0.131, Brier=0.0170, P&L théorique=$-82.94
- `kalshi_mid_baseline` (baseline) — p_yes=0.095, Brier=0.0090, P&L théorique=$-82.94 ⭐

Verdict run 615 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/615/report.json
