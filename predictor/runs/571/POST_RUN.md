**Run 571 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Jul 28, 2026?
Bin cible : `KXLOWTDEN-26JUL28-B68.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.537, Brier=0.2889, P&L réel=$-79.44
- `learned_v2` (challenger) — p_yes=0.872, Brier=0.7609, P&L théorique=$-79.44
- `kalshi_mid_baseline` (baseline) — p_yes=0.120, Brier=0.0144, P&L théorique=$-79.44 ⭐

Verdict run 571 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/571/report.json
