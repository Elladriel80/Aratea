**Run 019 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on May 22, 2026?
Bin cible : `KXLOWTCHI-26MAY22-B46.5` · Outcome : NO · Low observée (bin gagnant) : ≥51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.089, Brier=0.0080, P&L réel=$-0.45
- `learned_v2` (challenger) — p_yes=0.042, Brier=0.0017, P&L théorique=$-0.45
- `kalshi_mid_baseline` (baseline) — p_yes=0.030, Brier=0.0009, P&L théorique=$-0.45 ⭐

Verdict run 019 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/019/report.json
