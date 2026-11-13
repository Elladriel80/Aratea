**Run 1149 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Nov 11, 2026?
Bin cible : `KXLOWTMIA-26NOV11-B70.5` · Outcome : NO · Low observée (bin gagnant) : ≥75°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.229, Brier=0.0526, P&L réel=$-103.68
- `learned_v2` (challenger) — p_yes=0.306, Brier=0.0935, P&L théorique=$-103.68
- `kalshi_mid_baseline` (baseline) — p_yes=0.040, Brier=0.0016, P&L théorique=$-103.68 ⭐

Verdict run 1149 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1149/report.json
