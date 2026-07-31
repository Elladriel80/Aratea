**Run 573 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 30, 2026?
Bin cible : `KXLOWTNYC-26JUL30-B68.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.425, Brier=0.1810, P&L réel=$-82.07
- `learned_v2` (challenger) — p_yes=0.249, Brier=0.0619, P&L théorique=$-82.07
- `kalshi_mid_baseline` (baseline) — p_yes=0.175, Brier=0.0306, P&L théorique=$-82.07 ⭐

Verdict run 573 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/573/report.json
