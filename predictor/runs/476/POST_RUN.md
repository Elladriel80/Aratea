**Run 476 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 16, 2026?
Bin cible : `KXLOWTSFO-26JUL16-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.655, Brier=0.1192, P&L réel=$-69.12
- `learned_v2` (challenger) — p_yes=0.706, Brier=0.0865, P&L théorique=$-69.12
- `kalshi_mid_baseline` (baseline) — p_yes=0.865, Brier=0.0182, P&L théorique=$-69.12 ⭐

Verdict run 476 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/476/report.json
