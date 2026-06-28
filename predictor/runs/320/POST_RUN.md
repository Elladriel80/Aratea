**Run 320 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jun 26, 2026?
Bin cible : `KXLOWTSFO-26JUN26-B57.5` · Outcome : YES · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.384, Brier=0.3794, P&L réel=$-59.19
- `learned_v2` (challenger) — p_yes=0.188, Brier=0.6596, P&L théorique=$-59.19
- `kalshi_mid_baseline` (baseline) — p_yes=0.555, Brier=0.1980, P&L théorique=$-59.19 ⭐

Verdict run 320 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/320/report.json
