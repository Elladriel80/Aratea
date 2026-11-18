**Run 1185 — résolu YES · Multi-model A/B**

Event : Highest temperature in Washington DC on Nov 16, 2026?
Bin cible : `KXHIGHTDC-26NOV16-B57.5` · Outcome : YES · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.197, Brier=0.6455, P&L réel=$-135.42
- `learned_v2` (challenger) — p_yes=0.328, Brier=0.4513, P&L théorique=$-135.42
- `kalshi_mid_baseline` (baseline) — p_yes=0.695, Brier=0.0930, P&L théorique=$-135.42 ⭐

Verdict run 1185 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1185/report.json
