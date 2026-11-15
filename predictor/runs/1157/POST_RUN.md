**Run 1157 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Nov 13, 2026?
Bin cible : `KXLOWTLAX-26NOV13-B59.5` · Outcome : NO · Low observée (bin gagnant) : 61-62°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.081, Brier=0.0066, P&L réel=$+64.40
- `learned_v2` (challenger) — p_yes=0.040, Brier=0.0016, P&L théorique=$+64.40 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.400, Brier=0.1600, P&L théorique=$+64.40

Verdict run 1157 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1157/report.json
