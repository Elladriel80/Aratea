**Run 016 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on May 22, 2026?
Bin cible : `KXLOWTSFO-26MAY22-B53.5` · Outcome : NO · Low observée (bin gagnant) : 49-50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.441, Brier=0.1941, P&L réel=$-13.05
- `learned_v2` (challenger) — p_yes=0.759, Brier=0.5759, P&L théorique=$-13.05
- `kalshi_mid_baseline` (baseline) — p_yes=0.150, Brier=0.0225, P&L théorique=$-13.05 ⭐

Verdict run 016 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/016/report.json
