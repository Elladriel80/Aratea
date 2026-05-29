**Run 081 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on May 28, 2026?
Bin cible : `KXLOWTCHI-26MAY28-B55.5` · Outcome : YES · Low observée (bin gagnant) : 55-56°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.149, Brier=0.7249, P&L réel=$-21.28
- `learned_v2` (challenger) — p_yes=0.069, Brier=0.8666, P&L théorique=$-21.28
- `kalshi_mid_baseline` (baseline) — p_yes=0.335, Brier=0.4422, P&L théorique=$-21.28 ⭐

Verdict run 081 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/081/report.json
