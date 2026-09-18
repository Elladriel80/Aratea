**Run 735 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Sep 17, 2026?
Bin cible : `KXHIGHTSFO-26SEP17-B71.5` · Outcome : YES · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.236, Brier=0.5843, P&L réel=$-59.38
- `learned_v2` (challenger) — p_yes=0.286, Brier=0.5091, P&L théorique=$-59.38
- `kalshi_mid_baseline` (baseline) — p_yes=0.445, Brier=0.3080, P&L théorique=$-59.38 ⭐

Verdict run 735 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/735/report.json
