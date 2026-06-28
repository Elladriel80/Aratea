**Run 324 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 26, 2026?
Bin cible : `KXLOWTDC-26JUN26-B69.5` · Outcome : NO · Low observée (bin gagnant) : ≥72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.292, Brier=0.0854, P&L réel=$+41.92
- `learned_v2` (challenger) — p_yes=0.098, Brier=0.0096, P&L théorique=$+41.92 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.415, Brier=0.1722, P&L théorique=$+41.92

Verdict run 324 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/324/report.json
