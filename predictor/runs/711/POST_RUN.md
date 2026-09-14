**Run 711 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Sep 13, 2026?
Bin cible : `KXHIGHTSFO-26SEP13-B71.5` · Outcome : YES · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.231, Brier=0.5919, P&L réel=$-70.29
- `learned_v2` (challenger) — p_yes=0.040, Brier=0.9218, P&L théorique=$-70.29
- `kalshi_mid_baseline` (baseline) — p_yes=0.505, Brier=0.2450, P&L théorique=$-70.29 ⭐

Verdict run 711 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/711/report.json
