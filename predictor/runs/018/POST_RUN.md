**Run 018 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on May 22, 2026?
Bin cible : `KXLOWTCHI-26MAY22-B50.5` · Outcome : NO · Low observée (bin gagnant) : ≥51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.164, Brier=0.0269, P&L réel=$+7.70
- `learned_v2` (challenger) — p_yes=0.072, Brier=0.0053, P&L théorique=$+7.70 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.275, Brier=0.0756, P&L théorique=$+7.70

Verdict run 018 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/018/report.json
