**Run 1094 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Nov 2, 2026?
Bin cible : `KXHIGHTSFO-26NOV02-B66.5` · Outcome : NO · Low observée (bin gagnant) : 64-65°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.220, Brier=0.0482, P&L réel=$+31.85
- `learned_v2` (challenger) — p_yes=0.202, Brier=0.0409, P&L théorique=$+31.85 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.490, Brier=0.2401, P&L théorique=$+31.85

Verdict run 1094 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1094/report.json
