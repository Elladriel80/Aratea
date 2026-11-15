**Run 1160 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on Nov 13, 2026?
Bin cible : `KXLOWTBOS-26NOV13-B35.5` · Outcome : YES · Low observée (bin gagnant) : 35-36°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.123, Brier=0.7683, P&L réel=$+2319.36 ⭐
- `learned_v2` (challenger) — p_yes=0.078, Brier=0.8497, P&L théorique=$+2319.36
- `kalshi_mid_baseline` (baseline) — p_yes=0.040, Brier=0.9216, P&L théorique=$+2319.36

Verdict run 1160 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1160/report.json
