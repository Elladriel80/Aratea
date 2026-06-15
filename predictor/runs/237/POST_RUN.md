**Run 237 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Jun 14, 2026?
Bin cible : `KXLOWTSEA-26JUN14-B54.5` · Outcome : NO · Low observée (bin gagnant) : ≥59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.148, Brier=0.0221, P&L réel=$-4.15
- `learned_v2` (challenger) — p_yes=0.126, Brier=0.0158, P&L théorique=$-4.15
- `kalshi_mid_baseline` (baseline) — p_yes=0.050, Brier=0.0025, P&L théorique=$-4.15 ⭐

Verdict run 237 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/237/report.json
