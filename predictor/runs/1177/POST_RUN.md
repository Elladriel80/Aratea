**Run 1177 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Nov 16, 2026?
Bin cible : `KXLOWTCHI-26NOV16-B31.5` · Outcome : YES · Low observée (bin gagnant) : 31-32°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.170, Brier=0.6883, P&L réel=$-135.13
- `learned_v2` (challenger) — p_yes=0.278, Brier=0.5215, P&L théorique=$-135.13
- `kalshi_mid_baseline` (baseline) — p_yes=0.415, Brier=0.3422, P&L théorique=$-135.13 ⭐

Verdict run 1177 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1177/report.json
