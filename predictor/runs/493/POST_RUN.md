**Run 493 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 19, 2026?
Bin cible : `KXLOWTNYC-26JUL19-B69.5` · Outcome : NO · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.517, Brier=0.2674, P&L réel=$-60.48
- `learned_v2` (challenger) — p_yes=0.437, Brier=0.1912, P&L théorique=$-60.48
- `kalshi_mid_baseline` (baseline) — p_yes=0.360, Brier=0.1296, P&L théorique=$-60.48 ⭐

Verdict run 493 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/493/report.json
