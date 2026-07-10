**Run 413 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jul 9, 2026?
Bin cible : `KXLOWTLAX-26JUL09-B63.5` · Outcome : YES · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.303, Brier=0.4851, P&L réel=$-72.40
- `learned_v2` (challenger) — p_yes=0.121, Brier=0.7733, P&L théorique=$-72.40
- `kalshi_mid_baseline` (baseline) — p_yes=0.600, Brier=0.1600, P&L théorique=$-72.40 ⭐

Verdict run 413 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/413/report.json
