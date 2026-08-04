**Run 605 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Aug 3, 2026?
Bin cible : `KXLOWTNYC-26AUG03-B74.5` · Outcome : NO · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.653, Brier=0.4261, P&L réel=$-82.92
- `learned_v2` (challenger) — p_yes=0.710, Brier=0.5045, P&L théorique=$-82.92
- `kalshi_mid_baseline` (baseline) — p_yes=0.115, Brier=0.0132, P&L théorique=$-82.92 ⭐

Verdict run 605 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/605/report.json
