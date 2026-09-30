**Run 827 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Sep 29, 2026?
Bin cible : `KXLOWTLAX-26SEP29-B64.5` · Outcome : NO · Low observée (bin gagnant) : 62-63°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.621, Brier=0.3859, P&L réel=$-65.56
- `learned_v2` (challenger) — p_yes=0.726, Brier=0.5275, P&L théorique=$-65.56
- `kalshi_mid_baseline` (baseline) — p_yes=0.440, Brier=0.1936, P&L théorique=$-65.56 ⭐

Verdict run 827 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/827/report.json
