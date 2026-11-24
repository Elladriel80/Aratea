**Run 1191 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Nov 22, 2026?
Bin cible : `KXLOWTLAX-26NOV22-B51.5` · Outcome : NO · Low observée (bin gagnant) : 47-48°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.456, Brier=0.2078, P&L réel=$-136.08
- `learned_v2` (challenger) — p_yes=0.704, Brier=0.4954, P&L théorique=$-136.08
- `kalshi_mid_baseline` (baseline) — p_yes=0.210, Brier=0.0441, P&L théorique=$-136.08 ⭐

Verdict run 1191 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1191/report.json
