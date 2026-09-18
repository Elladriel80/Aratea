**Run 741 — résolu YES · Multi-model A/B**

Event : Highest temperature in Boston on Sep 17, 2026?
Bin cible : `KXHIGHTBOS-26SEP17-B76.5` · Outcome : YES · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.180, Brier=0.6724, P&L réel=$-59.60
- `learned_v2` (challenger) — p_yes=0.264, Brier=0.5416, P&L théorique=$-59.60
- `kalshi_mid_baseline` (baseline) — p_yes=0.315, Brier=0.4692, P&L théorique=$-59.60 ⭐

Verdict run 741 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/741/report.json
