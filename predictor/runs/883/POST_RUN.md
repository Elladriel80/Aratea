**Run 883 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Oct 5, 2026?
Bin cible : `KXLOWTMIA-26OCT05-B74.5` · Outcome : NO · Low observée (bin gagnant) : ≥79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.092, Brier=0.0084, P&L réel=$-48.86
- `learned_v2` (challenger) — p_yes=0.042, Brier=0.0018, P&L théorique=$-48.86
- `kalshi_mid_baseline` (baseline) — p_yes=0.035, Brier=0.0012, P&L théorique=$-48.86 ⭐

Verdict run 883 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/883/report.json
