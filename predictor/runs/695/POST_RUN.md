**Run 695 — résolu YES · Multi-model A/B**

Event : Highest temperature in Boston on Sep 11, 2026?
Bin cible : `KXHIGHTBOS-26SEP11-B78.5` · Outcome : YES · Low observée (bin gagnant) : 78-79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.254, Brier=0.5568, P&L réel=$-84.16
- `learned_v2` (challenger) — p_yes=0.404, Brier=0.3557, P&L théorique=$-84.16
- `kalshi_mid_baseline` (baseline) — p_yes=0.535, Brier=0.2162, P&L théorique=$-84.16 ⭐

Verdict run 695 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/695/report.json
