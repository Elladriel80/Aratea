**Run 265 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 18, 2026?
Bin cible : `KXLOWTDC-26JUN18-B71.5` · Outcome : NO · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.236, Brier=0.0555, P&L réel=$-47.84
- `learned_v2` (challenger) — p_yes=0.500, Brier=0.2500, P&L théorique=$-47.84
- `kalshi_mid_baseline` (baseline) — p_yes=0.160, Brier=0.0256, P&L théorique=$-47.84 ⭐

Verdict run 265 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/265/report.json
