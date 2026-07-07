**Run 392 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 6, 2026?
Bin cible : `KXLOWTSFO-26JUL06-B54.5` · Outcome : NO · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.318, Brier=0.1013, P&L réel=$-67.10
- `learned_v2` (challenger) — p_yes=0.108, Brier=0.0116, P&L théorique=$-67.10
- `kalshi_mid_baseline` (baseline) — p_yes=0.105, Brier=0.0110, P&L théorique=$-67.10 ⭐

Verdict run 392 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/392/report.json
