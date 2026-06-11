**Run 201 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Jun 9, 2026?
Bin cible : `KXLOWTSEA-26JUN09-B49.5` · Outcome : NO · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.288, Brier=0.0830, P&L réel=$-7.36
- `learned_v2` (challenger) — p_yes=0.188, Brier=0.0355, P&L théorique=$-7.36
- `kalshi_mid_baseline` (baseline) — p_yes=0.160, Brier=0.0256, P&L théorique=$-7.36 ⭐

Verdict run 201 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/201/report.json
