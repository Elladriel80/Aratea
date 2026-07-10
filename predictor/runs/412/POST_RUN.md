**Run 412 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 9, 2026?
Bin cible : `KXLOWTNYC-26JUL09-B69.5` · Outcome : NO · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.287, Brier=0.0822, P&L réel=$+43.50
- `learned_v2` (challenger) — p_yes=0.097, Brier=0.0093, P&L théorique=$+43.50 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.375, Brier=0.1406, P&L théorique=$+43.50

Verdict run 412 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/412/report.json
