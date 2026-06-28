**Run 318 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 26, 2026?
Bin cible : `KXLOWTNYC-26JUN26-B68.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.605, Brier=0.3660, P&L réel=$-59.13
- `learned_v2` (challenger) — p_yes=0.613, Brier=0.3763, P&L théorique=$-59.13
- `kalshi_mid_baseline` (baseline) — p_yes=0.365, Brier=0.1332, P&L théorique=$-59.13 ⭐

Verdict run 318 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/318/report.json
