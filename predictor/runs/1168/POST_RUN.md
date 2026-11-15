**Run 1168 — résolu YES · Multi-model A/B**

Event : Highest temperature in Washington DC on Nov 13, 2026?
Bin cible : `KXHIGHTDC-26NOV13-B51.5` · Outcome : YES · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.087, Brier=0.8329, P&L réel=$-96.52
- `learned_v2` (challenger) — p_yes=0.069, Brier=0.8673, P&L théorique=$-96.52
- `kalshi_mid_baseline` (baseline) — p_yes=0.620, Brier=0.1444, P&L théorique=$-96.52 ⭐

Verdict run 1168 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1168/report.json
