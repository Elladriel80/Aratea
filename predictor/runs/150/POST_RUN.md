**Run 150 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Jun 3, 2026?
Bin cible : `KXLOWTPHX-26JUN03-B74.5` · Outcome : NO · Low observée (bin gagnant) : ≥77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.159, Brier=0.0251, P&L réel=$-1.50
- `learned_v2` (challenger) — p_yes=0.192, Brier=0.0368, P&L théorique=$-1.50
- `kalshi_mid_baseline` (baseline) — p_yes=0.050, Brier=0.0025, P&L théorique=$-1.50 ⭐

Verdict run 150 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/150/report.json
