**Run 1192 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Nov 22, 2026?
Bin cible : `KXLOWTLAX-26NOV22-B47.5` · Outcome : YES · Low observée (bin gagnant) : 47-48°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.049, Brier=0.9053, P&L réel=$-135.88
- `learned_v2` (challenger) — p_yes=0.074, Brier=0.8570, P&L théorique=$-135.88
- `kalshi_mid_baseline` (baseline) — p_yes=0.210, Brier=0.6241, P&L théorique=$-135.88 ⭐

Verdict run 1192 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1192/report.json
