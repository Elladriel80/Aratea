**Run 629 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Aug 5, 2026?
Bin cible : `KXLOWTDC-26AUG05-B73.5` · Outcome : NO · Low observée (bin gagnant) : ≥74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.371, Brier=0.1374, P&L réel=$-72.28
- `learned_v2` (challenger) — p_yes=0.531, Brier=0.2825, P&L théorique=$-72.28
- `kalshi_mid_baseline` (baseline) — p_yes=0.305, Brier=0.0930, P&L théorique=$-72.28 ⭐

Verdict run 629 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/629/report.json
