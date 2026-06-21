**Run 279 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Jun 20, 2026?
Bin cible : `KXLOWTBOS-26JUN20-B58.5` · Outcome : NO · Low observée (bin gagnant) : ≥61°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.096, Brier=0.0092, P&L réel=$-30.28
- `learned_v2` (challenger) — p_yes=0.102, Brier=0.0103, P&L théorique=$-30.28
- `kalshi_mid_baseline` (baseline) — p_yes=0.035, Brier=0.0012, P&L théorique=$-30.28 ⭐

Verdict run 279 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/279/report.json
