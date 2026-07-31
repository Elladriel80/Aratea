**Run 581 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 30, 2026?
Bin cible : `KXLOWTCHI-26JUL30-B65.5` · Outcome : NO · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.333, Brier=0.1108, P&L réel=$-82.08
- `learned_v2` (challenger) — p_yes=0.158, Brier=0.0249, P&L théorique=$-82.08 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.240, Brier=0.0576, P&L théorique=$-82.08

Verdict run 581 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/581/report.json
