**Run 568 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Jul 28, 2026?
Bin cible : `KXLOWTMIA-26JUL28-B77.5` · Outcome : YES · Low observée (bin gagnant) : 77-78°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.252, Brier=0.5599, P&L réel=$-79.28
- `learned_v2` (challenger) — p_yes=0.038, Brier=0.9259, P&L théorique=$-79.28
- `kalshi_mid_baseline` (baseline) — p_yes=0.475, Brier=0.2756, P&L théorique=$-79.28 ⭐

Verdict run 568 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/568/report.json
