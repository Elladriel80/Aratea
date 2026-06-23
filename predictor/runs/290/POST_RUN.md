**Run 290 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jun 22, 2026?
Bin cible : `KXLOWTLAX-26JUN22-B58.5` · Outcome : NO · Low observée (bin gagnant) : ≥61°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.058, Brier=0.0033, P&L réel=$+5.95
- `learned_v2` (challenger) — p_yes=0.038, Brier=0.0014, P&L théorique=$+5.95 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.145, Brier=0.0210, P&L théorique=$+5.95

Verdict run 290 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/290/report.json
