**Run 044 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on May 24, 2026?
Bin cible : `KXLOWTMIA-26MAY24-B76.5` · Outcome : NO · Low observée (bin gagnant) : 78-79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.191, Brier=0.0365, P&L réel=$-3.48
- `learned_v2` (challenger) — p_yes=0.095, Brier=0.0091, P&L théorique=$-3.48 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.120, Brier=0.0144, P&L théorique=$-3.48

Verdict run 044 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/044/report.json
