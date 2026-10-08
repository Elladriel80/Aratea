**Run 890 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Oct 7, 2026?
Bin cible : `KXLOWTLAX-26OCT07-B72.5` · Outcome : NO · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.525, Brier=0.2761, P&L réel=$-57.75
- `learned_v2` (challenger) — p_yes=0.524, Brier=0.2747, P&L théorique=$-57.75
- `kalshi_mid_baseline` (baseline) — p_yes=0.330, Brier=0.1089, P&L théorique=$-57.75 ⭐

Verdict run 890 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/890/report.json
