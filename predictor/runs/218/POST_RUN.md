**Run 218 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 12, 2026?
Bin cible : `KXLOWTDC-26JUN12-B73.5` · Outcome : NO · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.183, Brier=0.0336, P&L réel=$+10.20
- `learned_v2` (challenger) — p_yes=0.064, Brier=0.0041, P&L théorique=$+10.20 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.300, Brier=0.0900, P&L théorique=$+10.20

Verdict run 218 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/218/report.json
