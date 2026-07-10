**Run 420 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Jul 9, 2026?
Bin cible : `KXLOWTMIA-26JUL09-B83.5` · Outcome : NO · Low observée (bin gagnant) : 81-82°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.470, Brier=0.2209, P&L réel=$-72.50
- `learned_v2` (challenger) — p_yes=0.853, Brier=0.7270, P&L théorique=$-72.50
- `kalshi_mid_baseline` (baseline) — p_yes=0.250, Brier=0.0625, P&L théorique=$-72.50 ⭐

Verdict run 420 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/420/report.json
