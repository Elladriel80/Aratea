**Run 100 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on May 30, 2026?
Bin cible : `KXLOWTLAX-26MAY30-B58.5` · Outcome : NO · Low observée (bin gagnant) : ≥59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.337, Brier=0.1136, P&L réel=$+20.91
- `learned_v2` (challenger) — p_yes=0.193, Brier=0.0371, P&L théorique=$+20.91 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.510, Brier=0.2601, P&L théorique=$+20.91

Verdict run 100 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/100/report.json
