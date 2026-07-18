**Run 481 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 17, 2026?
Bin cible : `KXLOWTCHI-26JUL17-B73.5` · Outcome : NO · Low observée (bin gagnant) : ≥76°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.471, Brier=0.2221, P&L réel=$-70.32
- `learned_v2` (challenger) — p_yes=0.341, Brier=0.1160, P&L théorique=$-70.32
- `kalshi_mid_baseline` (baseline) — p_yes=0.205, Brier=0.0420, P&L théorique=$-70.32 ⭐

Verdict run 481 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/481/report.json
