**Run 913 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Oct 9, 2026?
Bin cible : `KXLOWTMIA-26OCT09-B77.5` · Outcome : NO · Low observée (bin gagnant) : ≥80°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.347, Brier=0.1205, P&L réel=$-44.66
- `learned_v2` (challenger) — p_yes=0.136, Brier=0.0185, P&L théorique=$-44.66
- `kalshi_mid_baseline` (baseline) — p_yes=0.110, Brier=0.0121, P&L théorique=$-44.66 ⭐

Verdict run 913 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/913/report.json
