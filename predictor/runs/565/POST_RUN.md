**Run 565 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 28, 2026?
Bin cible : `KXLOWTCHI-26JUL28-B68.5` · Outcome : YES · Low observée (bin gagnant) : 68-69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.440, Brier=0.3139, P&L réel=$-79.20
- `learned_v2` (challenger) — p_yes=0.350, Brier=0.4224, P&L théorique=$-79.20
- `kalshi_mid_baseline` (baseline) — p_yes=0.520, Brier=0.2304, P&L théorique=$-79.20 ⭐

Verdict run 565 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/565/report.json
