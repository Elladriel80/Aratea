**Run 056 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on May 26, 2026?
Bin cible : `KXLOWTLAX-26MAY26-B57.5` · Outcome : YES · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.373, Brier=0.3933, P&L réel=$-20.67
- `learned_v2` (challenger) — p_yes=0.176, Brier=0.6797, P&L théorique=$-20.67
- `kalshi_mid_baseline` (baseline) — p_yes=0.470, Brier=0.2809, P&L théorique=$-20.67 ⭐

Verdict run 056 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/056/report.json
