**Run 703 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on Sep 13, 2026?
Bin cible : `KXLOWTBOS-26SEP13-B62.5` · Outcome : YES · Low observée (bin gagnant) : 62-63°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.325, Brier=0.4561, P&L réel=$-70.62
- `learned_v2` (challenger) — p_yes=0.471, Brier=0.2798, P&L théorique=$-70.62 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.465, Brier=0.2862, P&L théorique=$-70.62

Verdict run 703 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/703/report.json
