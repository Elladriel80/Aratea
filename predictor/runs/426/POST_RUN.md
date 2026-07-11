**Run 426 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 10, 2026?
Bin cible : `KXLOWTSFO-26JUL10-B56.5` · Outcome : NO · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.225, Brier=0.0508, P&L réel=$-89.88
- `learned_v2` (challenger) — p_yes=0.098, Brier=0.0096, P&L théorique=$-89.88
- `kalshi_mid_baseline` (baseline) — p_yes=0.060, Brier=0.0036, P&L théorique=$-89.88 ⭐

Verdict run 426 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/426/report.json
