**Run 1159 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Nov 13, 2026?
Bin cible : `KXLOWTDC-26NOV13-B37.5` · Outcome : NO · Low observée (bin gagnant) : 41-42°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.123, Brier=0.0153, P&L réel=$-96.64
- `learned_v2` (challenger) — p_yes=0.092, Brier=0.0085, P&L théorique=$-96.64
- `kalshi_mid_baseline` (baseline) — p_yes=0.035, Brier=0.0012, P&L théorique=$-96.64 ⭐

Verdict run 1159 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1159/report.json
