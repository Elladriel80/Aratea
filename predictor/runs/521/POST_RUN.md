**Run 521 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jul 22, 2026?
Bin cible : `KXLOWTLAX-26JUL22-B68.5` · Outcome : YES · Low observée (bin gagnant) : 68-69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.269, Brier=0.5340, P&L réel=$-50.00
- `learned_v2` (challenger) — p_yes=0.076, Brier=0.8535, P&L théorique=$-50.00
- `kalshi_mid_baseline` (baseline) — p_yes=0.375, Brier=0.3906, P&L théorique=$-50.00 ⭐

Verdict run 521 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/521/report.json
