**Run 1187 — résolu YES · Multi-model A/B**

Event : Highest temperature in Boston on Nov 16, 2026?
Bin cible : `KXHIGHTBOS-26NOV16-B51.5` · Outcome : YES · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.228, Brier=0.5954, P&L réel=$+0.00
- `learned_v2` (challenger) — p_yes=0.378, Brier=0.3864, P&L théorique=$+0.00
- `kalshi_mid_baseline` (baseline) — p_yes=0.570, Brier=0.1849, P&L théorique=$+0.00 ⭐

Verdict run 1187 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1187/report.json
