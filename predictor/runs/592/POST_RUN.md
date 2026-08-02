**Run 592 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Aug 1, 2026?
Bin cible : `KXLOWTLAX-26AUG01-B66.5` · Outcome : YES · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.257, Brier=0.5518, P&L réel=$-78.98
- `learned_v2` (challenger) — p_yes=0.089, Brier=0.8302, P&L théorique=$-78.98
- `kalshi_mid_baseline` (baseline) — p_yes=0.325, Brier=0.4556, P&L théorique=$-78.98 ⭐

Verdict run 592 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/592/report.json
