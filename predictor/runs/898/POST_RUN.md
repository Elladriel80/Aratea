**Run 898 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Oct 7, 2026?
Bin cible : `KXLOWTSEA-26OCT07-B47.5` · Outcome : NO · Low observée (bin gagnant) : ≥52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.051, Brier=0.0026, P&L réel=$-44.13
- `learned_v2` (challenger) — p_yes=0.074, Brier=0.0055, P&L théorique=$-44.13
- `kalshi_mid_baseline` (baseline) — p_yes=0.030, Brier=0.0009, P&L théorique=$-44.13 ⭐

Verdict run 898 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/898/report.json
