**Run 211 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jun 12, 2026?
Bin cible : `KXLOWTLAX-26JUN12-B59.5` · Outcome : NO · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.093, Brier=0.0086, P&L réel=$-19.62
- `learned_v2` (challenger) — p_yes=0.017, Brier=0.0003, P&L théorique=$-19.62 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.030, Brier=0.0009, P&L théorique=$-19.62

Verdict run 211 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/211/report.json
