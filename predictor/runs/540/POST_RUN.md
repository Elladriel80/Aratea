**Run 540 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 24, 2026?
Bin cible : `KXLOWTSFO-26JUL24-B58.5` · Outcome : NO · Low observée (bin gagnant) : ≥59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.428, Brier=0.1829, P&L réel=$+25.16
- `learned_v2` (challenger) — p_yes=0.263, Brier=0.0690, P&L théorique=$+25.16 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.645, Brier=0.4160, P&L théorique=$+25.16

Verdict run 540 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/540/report.json
