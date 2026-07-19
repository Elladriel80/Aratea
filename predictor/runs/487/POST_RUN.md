**Run 487 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 18, 2026?
Bin cible : `KXLOWTNYC-26JUL18-B74.5` · Outcome : NO · Low observée (bin gagnant) : 68-69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.210, Brier=0.0440, P&L réel=$-62.16
- `learned_v2` (challenger) — p_yes=0.061, Brier=0.0037, P&L théorique=$-62.16
- `kalshi_mid_baseline` (baseline) — p_yes=0.060, Brier=0.0036, P&L théorique=$-62.16 ⭐

Verdict run 487 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/487/report.json
