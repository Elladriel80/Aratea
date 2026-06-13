**Run 219 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on Jun 12, 2026?
Bin cible : `KXLOWTBOS-26JUN12-B68.5` · Outcome : YES · Low observée (bin gagnant) : 68-69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.119, Brier=0.7767, P&L réel=$-24.00
- `learned_v2` (challenger) — p_yes=0.178, Brier=0.6750, P&L théorique=$-24.00
- `kalshi_mid_baseline` (baseline) — p_yes=0.250, Brier=0.5625, P&L théorique=$-24.00 ⭐

Verdict run 219 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/219/report.json
