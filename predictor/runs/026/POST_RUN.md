**Run 026 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on May 22, 2026?
Bin cible : `KXLOWTDEN-26MAY22-B43.5` · Outcome : NO · Low observée (bin gagnant) : ≤39°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.136, Brier=0.0185, P&L réel=$-1.26
- `learned_v2` (challenger) — p_yes=0.223, Brier=0.0499, P&L théorique=$-1.26
- `kalshi_mid_baseline` (baseline) — p_yes=0.070, Brier=0.0049, P&L théorique=$-1.26 ⭐

Verdict run 026 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/026/report.json
