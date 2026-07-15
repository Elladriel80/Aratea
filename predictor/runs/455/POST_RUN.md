**Run 455 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jul 14, 2026?
Bin cible : `KXLOWTLAX-26JUL14-B66.5` · Outcome : YES · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.540, Brier=0.2116, P&L réel=$-72.59
- `learned_v2` (challenger) — p_yes=0.489, Brier=0.2606, P&L théorique=$-72.59
- `kalshi_mid_baseline` (baseline) — p_yes=0.695, Brier=0.0930, P&L théorique=$-72.59 ⭐

Verdict run 455 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/455/report.json
