**Run 921 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Oct 11, 2026?
Bin cible : `KXLOWTSFO-26OCT11-B51.5` · Outcome : YES · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.363, Brier=0.4052, P&L réel=$-45.14
- `learned_v2` (challenger) — p_yes=0.160, Brier=0.7051, P&L théorique=$-45.14
- `kalshi_mid_baseline` (baseline) — p_yes=0.695, Brier=0.0930, P&L théorique=$-45.14 ⭐

Verdict run 921 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/921/report.json
