**Run 737 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Sep 17, 2026?
Bin cible : `KXHIGHTSFO-26SEP17-B69.5` · Outcome : NO · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.248, Brier=0.0615, P&L réel=$-59.67
- `learned_v2` (challenger) — p_yes=0.268, Brier=0.0718, P&L théorique=$-59.67
- `kalshi_mid_baseline` (baseline) — p_yes=0.170, Brier=0.0289, P&L théorique=$-59.67 ⭐

Verdict run 737 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/737/report.json
