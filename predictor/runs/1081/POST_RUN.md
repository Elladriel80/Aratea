**Run 1081 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Nov 2, 2026?
Bin cible : `KXLOWTNYC-26NOV02-B45.5` · Outcome : NO · Low observée (bin gagnant) : 43-44°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.373, Brier=0.1395, P&L réel=$-116.34
- `learned_v2` (challenger) — p_yes=0.690, Brier=0.4758, P&L théorique=$-116.34
- `kalshi_mid_baseline` (baseline) — p_yes=0.070, Brier=0.0049, P&L théorique=$-116.34 ⭐

Verdict run 1081 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1081/report.json
