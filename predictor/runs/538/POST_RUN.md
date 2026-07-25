**Run 538 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jul 24, 2026?
Bin cible : `KXLOWTLAX-26JUL24-B67.5` · Outcome : YES · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.115, Brier=0.7835, P&L réel=$-56.58
- `learned_v2` (challenger) — p_yes=0.022, Brier=0.9555, P&L théorique=$-56.58
- `kalshi_mid_baseline` (baseline) — p_yes=0.225, Brier=0.6006, P&L théorique=$-56.58 ⭐

Verdict run 538 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/538/report.json
