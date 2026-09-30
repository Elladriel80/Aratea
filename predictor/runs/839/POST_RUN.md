**Run 839 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Sep 29, 2026?
Bin cible : `KXHIGHTSFO-26SEP29-B79.5` · Outcome : YES · Low observée (bin gagnant) : 79-80°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.133, Brier=0.7526, P&L réel=$-65.10
- `learned_v2` (challenger) — p_yes=0.235, Brier=0.5858, P&L théorique=$-65.10 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.225, Brier=0.6006, P&L théorique=$-65.10

Verdict run 839 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/839/report.json
